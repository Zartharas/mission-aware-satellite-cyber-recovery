// passive_nos_engine_time_witness.cpp
//
// WP4 passive NOS Engine time-witness.
//
// Subscribes passively to authoritative NOS Engine time ticks using the pinned
// supported NosEngine::Client::Bus time-tick callback API. It NEVER calls
// set_time, enable_set_time, a command send method, a request/reply method, a
// DataNode or CommandNode transmit method, or any event-injection interface.
//
// Every emitted record uses clock_gettime(CLOCK_MONOTONIC), the same clock
// basis already used by scripts/radio_socket_metadata_shim.c.
//
// Records are newline-delimited JSON objects with exactly four keys:
//   sequence      integer, starting at 1, increasing by exactly 1
//   monotonic_ns  non-negative integer, never decreases
//   tick          non-negative integer for "tick" records, else null
//   state         one of "connected", "tick", "disconnected"
//
// The evidence file is opened with owner-only mode 0600, append behaviour,
// and close-on-exec where supported. Record emission is thread-safe.
// Clean termination is supported through SIGINT and SIGTERM using a
// signal-safe stop flag.
//
// Dependency injection is used for the monotonic clock and record sink so the
// built-in --self-test does not rely on live timing and never constructs a
// NOS Engine client, opens a network socket, or invokes Docker.
//
// Compilation (pin):
//   g++ -std=c++14 -Wall -Wextra -Werror -I/usr/include
//       scripts/passive_nos_engine_time_witness.cpp
//       -lnos_engine_client -lnos_engine_common
//       -o passive_nos_engine_time_witness
//
// Contract version: 0.4.5 (PASSIVE_TIME_WITNESS_IMPLEMENTED_STATIC_GATE_PENDING)
// Contract status: closed runtime gate. No runtime authorized.

#include <Client/Bus.hpp>
#include <Client/types.hpp>
#include <Common/types.hpp>

#include <cerrno>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fcntl.h>
#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <vector>

#include <csignal>

namespace {

// ---------------------------------------------------------------------------
// Signal-safe stop flag.
// ---------------------------------------------------------------------------

volatile sig_atomic_t g_stop_requested = 0;

extern "C" void stop_signal_handler(int signum) {
  (void)signum;
  g_stop_requested = 1;
}

// ---------------------------------------------------------------------------
// Elided-message helpers. Errors never echo the connection string or any
// forbidden evidence field. Generic placeholders keep the public output free
// of URIs, hostnames, ports, bus names, process IDs, thread IDs, payloads,
// packet lengths, packet hashes, command data, policy state, or wall-clock
// time.
// ---------------------------------------------------------------------------

void emit_user_error(const char *what) {
  std::cerr << "passive_nos_engine_time_witness: error: " << what << "\n";
}

// ---------------------------------------------------------------------------
// Clock abstraction (dependency injection).
//
// The live clock uses clock_gettime(CLOCK_MONOTONIC), the same clock basis
// already used by scripts/radio_socket_metadata_shim.c. The self-test injects
// a deterministic synthetic clock so determinism does not depend on live
// timing.
// ---------------------------------------------------------------------------

using MonotonicNs = std::int64_t;

struct MonotonicClock {
  virtual ~MonotonicClock() {}
  virtual MonotonicNs now_ns() = 0;
};

class LiveMonotonicClock : public MonotonicClock {
 public:
  MonotonicNs now_ns() override {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
      // We never surface raw errno text into retained evidence; signal
      // failure to the caller as a pseudo-timestamp suppression marker.
      return -1;
    }
    return static_cast<MonotonicNs>(ts.tv_sec) * 1000000000LL +
           static_cast<MonotonicNs>(ts.tv_nsec);
  }
};

class SyntheticMonotonicClock : public MonotonicClock {
 public:
  explicit SyntheticMonotonicClock(std::vector<MonotonicNs> sequence)
      : sequence_(std::move(sequence)), index_(0) {}

  MonotonicNs now_ns() override {
    if (index_ < sequence_.size()) {
      return sequence_[index_++];
    }
    if (sequence_.empty()) {
      return 0;
    }
    MonotonicNs last = sequence_.back();
    MonotonicNs next = last + 1000000000LL;  // +1 s, strictly increasing
    sequence_.push_back(next);
    ++index_;
    return next;
  }

 private:
  std::vector<MonotonicNs> sequence_;
  std::size_t index_;
};

// ---------------------------------------------------------------------------
// Record sink abstraction (dependency injection).
//
// The live sink is an owner-only, append, close-on-exec file. The self-test
// injects an in-memory sink so it does not touch any filesystem path.
// ---------------------------------------------------------------------------

struct Record {
  std::uint64_t sequence;
  MonotonicNs monotonic_ns;  // never used directly as evidence beyond schema
  bool has_tick;
  std::int64_t tick;  // valid only when has_tick is true
  std::string state;  // "connected" | "tick" | "disconnected"
};

class RecordSink {
 public:
  virtual ~RecordSink() {}
  virtual bool open() = 0;
  virtual bool write(const std::string &line) = 0;
  virtual void close() = 0;
};

class FileRecordSink : public RecordSink {
 public:
  explicit FileRecordSink(std::string path) : path_(std::move(path)), fd_(-1) {}

  ~FileRecordSink() override { close(); }

  bool open() override {
    // Owner-only mode 0600, append behaviour, close-on-exec where supported.
    fd_ = ::open(path_.c_str(),
                 O_WRONLY | O_APPEND | O_CREAT | O_CLOEXEC,
                 S_IRUSR | S_IWUSR);
    if (fd_ < 0) {
      emit_user_error("evidence sink open failed");
      return false;
    }
    return true;
  }

  bool write(const std::string &line) override {
    if (fd_ < 0) {
      return false;
    }
    const char *data = line.data();
    std::size_t remaining = line.size();
    while (remaining > 0) {
      ssize_t wrote = ::write(fd_, data, remaining);
      if (wrote < 0) {
        if (errno == EINTR) {
          continue;
        }
        emit_user_error("evidence sink write failed");
        return false;
      }
      data += wrote;
      remaining -= static_cast<std::size_t>(wrote);
    }
    return true;
  }

  void close() override {
    if (fd_ >= 0) {
      ::close(fd_);
      fd_ = -1;
    }
  }

 private:
  std::string path_;
  int fd_;
};

class MemoryRecordSink : public RecordSink {
 public:
  bool open() override { return true; }
  bool write(const std::string &line) override {
    lines_.push_back(line);
    return true;
  }
  void close() override {}
  const std::vector<std::string> &lines() const { return lines_; }

 private:
  std::vector<std::string> lines_;
};

// ---------------------------------------------------------------------------
// JSON serialization with the exact permitted key schema.
//
// Every emitted object contains exactly four keys and nothing else. We never
// emit connection strings, hostnames, ports, bus names, process IDs, thread
// IDs, payloads, packet lengths, packet hashes, command data, policy state,
// or wall-clock time.
// ---------------------------------------------------------------------------

std::string escape_json_string(const std::string &in) {
  std::string out;
  out.reserve(in.size() + 2);
  for (char ch : in) {
    switch (ch) {
      case '"': out += "\\\""; break;
      case '\\': out += "\\\\"; break;
      case '\n': out += "\\n"; break;
      case '\r': out += "\\r"; break;
      case '\t': out += "\\t"; break;
      default: out += ch; break;
    }
  }
  return out;
}

std::string format_record(const Record &r) {
  std::ostringstream oss;
  oss << "{\"sequence\":" << r.sequence << ",\"monotonic_ns\":";
  if (r.monotonic_ns < 0) {
    // Schema requires non-negative integer; treat unavailable monotonic time
    // as 0 rather than surfacing forbidden diagnostics in evidence.
    oss << 0;
  } else {
    oss << r.monotonic_ns;
  }
  oss << ",\"tick\":";
  if (r.has_tick) {
    oss << r.tick;
  } else {
    oss << "null";
  }
  oss << ",\"state\":\"" << escape_json_string(r.state) << "\"}";
  return oss.str();
}

// ---------------------------------------------------------------------------
// Witness core. Thread-safe sequence issue and record emission.
// ---------------------------------------------------------------------------

class PassiveTimeWitness {
 public:
  PassiveTimeWitness(std::shared_ptr<MonotonicClock> clock,
                     std::shared_ptr<RecordSink> sink)
      : clock_(std::move(clock)),
        sink_(std::move(sink)),
        sequence_(0),
        last_state_(""),
        last_tick_value_(0),
        has_last_tick_(false) {}

  // Emit a connection-state transition only when the state changes.
  void emit_state_transition(const std::string &state) {
    std::lock_guard<std::mutex> guard(mutex_);
    if (state == last_state_) {
      return;
    }
    Record rec;
    rec.sequence = ++sequence_;
    rec.monotonic_ns = clock_->now_ns();
    rec.has_tick = false;
    rec.tick = 0;
    rec.state = state;
    emit_locked(rec);
    last_state_ = state;
  }

  // Emit a tick record. Authoritative tick values never decrease.
  void emit_tick(std::int64_t tick_value) {
    std::lock_guard<std::mutex> guard(mutex_);
    if (has_last_tick_ && tick_value < last_tick_value_) {
      return;  // never decrease authoritative tick values
    }
    Record rec;
    rec.sequence = ++sequence_;
    rec.monotonic_ns = clock_->now_ns();
    rec.has_tick = true;
    rec.tick = tick_value;
    rec.state = "tick";
    emit_locked(rec);
    last_state_ = "tick";
    last_tick_value_ = tick_value;
    has_last_tick_ = true;
  }

  bool open_sink() {
    std::lock_guard<std::mutex> guard(mutex_);
    return sink_->open();
  }

  void close_sink() {
    std::lock_guard<std::mutex> guard(mutex_);
    sink_->close();
  }

 private:
  void emit_locked(const Record &rec) {
    std::string line = format_record(rec);
    line += "\n";
    (void)sink_->write(line);
  }

  std::shared_ptr<MonotonicClock> clock_;
  std::shared_ptr<RecordSink> sink_;
  std::mutex mutex_;
  std::uint64_t sequence_;
  std::string last_state_;
  std::int64_t last_tick_value_;
  bool has_last_tick_;
};

// ---------------------------------------------------------------------------
// Pinned passive subscriber adapter.
//
// Uses the pinned supported NosEngine::Client::Bus time-tick callback API
// exactly as generic-radio and other pinned sims do. We never call set_time,
// enable_set_time, a command send method, a request/reply method, a DataNode
// or CommandNode transmit method, or any event-injection interface.
// ---------------------------------------------------------------------------

using NosEngine::Client::Bus;
using NosEngine::Common::SimTime;

class PinnedBusSubscriber {
 public:
  PinnedBusSubscriber(std::shared_ptr<Bus> bus,
                      PassiveTimeWitness *witness)
      : bus_(std::move(bus)), witness_(witness), callback_id_() {}

  void start() {
    // Passive subscribe: observe authoritative time ticks only.
    callback_id_ = bus_->add_time_tick_callback(
        [this](SimTime time) { on_tick(static_cast<std::int64_t>(time)); });
  }

  ~PinnedBusSubscriber() {
    try {
      bus_->remove_time_tick_callback(callback_id_);
    } catch (...) {
      // Passive subscriber teardown failures are not surfaced as evidence.
    }
  }

  bool is_connected() const {
    try {
      return bus_->is_connected();
    } catch (...) {
      return false;
    }
  }

 private:
  void on_tick(std::int64_t tick_value) {
    if (witness_ == nullptr) {
      return;
    }
    witness_->emit_tick(tick_value);
  }

  std::shared_ptr<Bus> bus_;
  PassiveTimeWitness *witness_;
  NosEngine::Client::TimeTickCallbackId callback_id_;
};

// ---------------------------------------------------------------------------
// Self-test. Deterministic, no NOS Engine client, no socket, no Docker,
// synthetic monotonic timestamps. Exercises connected, >= 3 increasing ticks,
// and disconnected. Proves exact key schema and state/tick rules.
// ---------------------------------------------------------------------------

int run_self_test() {
  // Deterministic synthetic monotonic timestamps (ns), strictly increasing.
  std::vector<MonotonicNs> synthetic = {
      1000000000LL,  // +1.000 s  (connected)
      1100000000LL,  // +1.100 s  (tick 0)
      1200000000LL,  // +1.200 s  (tick 1)
      1300000000LL,  // +1.300 s  (tick 2)
      1400000000LL,  // +1.400 s  (disconnected)
  };
  auto clock = std::make_shared<SyntheticMonotonicClock>(std::move(synthetic));
  auto sink = std::make_shared<MemoryRecordSink>();
  PassiveTimeWitness witness(clock, sink);

  if (!witness.open_sink()) {
    emit_user_error("self-test: sink open failed");
    return 1;
  }

  witness.emit_state_transition("connected");
  witness.emit_tick(0);
  witness.emit_tick(1);
  witness.emit_tick(2);
  witness.emit_state_transition("disconnected");

  witness.close_sink();

  const std::vector<std::string> &lines = sink->lines();
  if (lines.size() != 5) {
    std::cerr << "self-test: expected 5 records, saw " << lines.size() << "\n";
    return 1;
  }

  // Validate exact key schema and state/tick rules inline.
  const std::string required_keys[] = {"\"sequence\"", "\"monotonic_ns\"",
                                       "\"tick\"", "\"state\""};
  std::int64_t prev_monotonic = -1;
  std::uint64_t prev_sequence = 0;
  std::int64_t prev_tick = -1;
  const char *expected_states[] = {"connected", "tick", "tick", "tick",
                                   "disconnected"};
  for (std::size_t i = 0; i < lines.size(); ++i) {
    const std::string &line = lines[i];
    // Every line must be a single JSON object – one per line. The sink adds
    // a trailing newline; tolerate it.
    std::string trimmed = line;
    while (!trimmed.empty() && (trimmed.back() == '\n' || trimmed.back() == '\r')) {
      trimmed.pop_back();
    }
    if (trimmed.empty()) {
      std::cerr << "self-test: empty record at line " << (i + 1) << "\n";
      return 1;
    }
    for (const std::string &key : required_keys) {
      if (trimmed.find(key) == std::string::npos) {
        std::cerr << "self-test: missing key " << key << " at line "
                  << (i + 1) << "\n";
        return 1;
      }
    }
    // Exactly four separators means at most four keys with matching braces.
    if (trimmed.front() != '{' || trimmed.back() != '}') {
      std::cerr << "self-test: record " << (i + 1) << " is not a JSON object\n";
      return 1;
    }
    std::size_t key_count = 0;
    std::size_t pos = 0;
    while ((pos = trimmed.find("\":", pos)) != std::string::npos) {
      ++key_count;
      pos += 2;
    }
    if (key_count != 4) {
      std::cerr << "self-test: record " << (i + 1) << " has " << key_count
                << " key separators, expected 4\n";
      return 1;
    }
    // sequence: integer starting at 1 and increasing by exactly 1.
    char prefix[32];
    std::snprintf(prefix, sizeof(prefix), "{\"sequence\":%lu,",
                  static_cast<unsigned long>(i + 1));
    if (trimmed.rfind(prefix, 0) != 0) {
      std::cerr << "self-test: sequence rule failed at line " << (i + 1)
                << ": expected " << prefix << " prefix\n";
      return 1;
    }
    // state value must match deterministic expected sequence.
    std::string state_marker = "\"state\":\"";
    state_marker += expected_states[i];
    state_marker += "\"}";
    if (trimmed.find(state_marker) == std::string::npos) {
      std::cerr << "self-test: state mismatch at line " << (i + 1) << "\n";
      return 1;
    }
    // monotonic_ns: non-negative integer and never decreases.
    std::size_t mono_pos = trimmed.find("\"monotonic_ns\":");
    if (mono_pos == std::string::npos) {
      std::cerr << "self-test: monotonic_ns missing at line " << (i + 1)
                << "\n";
      return 1;
    }
    mono_pos += std::string("\"monotonic_ns\":").size();
    std::int64_t mono_val = 0;
    {
      std::size_t end = mono_pos;
      while (end < trimmed.size() && trimmed[end] >= '0' &&
             trimmed[end] <= '9') {
        mono_val = mono_val * 10 + (trimmed[end] - '0');
        ++end;
      }
      if (end == mono_pos) {
        std::cerr << "self-test: monotonic_ns not numeric at line "
                  << (i + 1) << "\n";
        return 1;
      }
    }
    if (mono_val < 0) {
      std::cerr << "self-test: monotonic_ns negative at line " << (i + 1)
                << "\n";
      return 1;
    }
    if (mono_val < prev_monotonic) {
      std::cerr << "self-test: monotonic_ns decreased at line " << (i + 1)
                << "\n";
      return 1;
    }
    prev_monotonic = mono_val;
    prev_sequence = static_cast<std::uint64_t>(i + 1);
    // tick rule: null for connected/disconnected, non-negative integer
    // for tick records. Authoritative tick values never decrease.
    std::size_t tick_pos = trimmed.find("\"tick\":");
    if (tick_pos == std::string::npos) {
      std::cerr << "self-test: tick key missing at line " << (i + 1) << "\n";
      return 1;
    }
    tick_pos += std::string("\"tick\":").size();
    if (trimmed.compare(tick_pos, 4, "null") == 0) {
      if (i == 1 || i == 2 || i == 3) {
        std::cerr << "self-test: tick null where integer expected at line "
                  << (i + 1) << "\n";
        return 1;
      }
    } else {
      if (i == 0 || i == 4) {
        std::cerr << "self-test: tick integer where null expected at line "
                  << (i + 1) << "\n";
        return 1;
      }
      std::int64_t tick_val = 0;
      std::size_t end = tick_pos;
      while (end < trimmed.size() && trimmed[end] >= '0' &&
             trimmed[end] <= '9') {
        tick_val = tick_val * 10 + (trimmed[end] - '0');
        ++end;
      }
      if (tick_val < 0) {
        std::cerr << "self-test: negative tick at line " << (i + 1) << "\n";
        return 1;
      }
      if (tick_val < prev_tick) {
        std::cerr << "self-test: authoritative tick decreased at line "
                  << (i + 1) << "\n";
        return 1;
      }
      prev_tick = tick_val;
    }
  }

  if (prev_sequence != 5) {
    std::cerr << "self-test: final sequence mismatch\n";
    return 1;
  }

  // Print the trace records for downstream validation, then the pass marker.
  for (const std::string &line : lines) {
    std::cout << line;
    if (line.empty() || line.back() != '\n') {
      std::cout << "\n";
    }
  }
  std::cout << "PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS" << std::endl;
  return 0;
}

// ---------------------------------------------------------------------------
// Live subscriber entrypoint. Used only when not running --self-test.
//
// NOTE: the runtime gate is closed in the current 0.4.5 contract. This
// entrypoint is a compile-only implementation candidate; it must not be
// executed against a live NOS Engine server in this phase. The static
// verifier exercises only --self-test with networking disabled.
// ---------------------------------------------------------------------------

int run_live(int argc, char **argv) {
  if (argc < 3) {
    emit_user_error(
        "usage: passive_nos_engine_time_witness <evidence_path> <uri> [name]");
    return 2;
  }
  std::string evidence_path = argv[1];
  std::string uri = argv[2];
  std::string name = (argc >= 4) ? argv[3] : "passive-time-witness";
  (void)name;

  // Register signal handlers for clean termination using a signal-safe flag.
  std::signal(SIGINT, stop_signal_handler);
  std::signal(SIGTERM, stop_signal_handler);

  auto clock = std::make_shared<LiveMonotonicClock>();
  auto sink = std::make_shared<FileRecordSink>(evidence_path);
  PassiveTimeWitness witness(clock, sink);
  if (!witness.open_sink()) {
    return 1;
  }

  // Construct the pinned passive subscriber. We never call set_time,
  // enable_set_time, command send, request/reply, DataNode/CommandNode
  // transmit, or event injection.
  std::shared_ptr<Bus> bus;
  try {
    bus = std::make_shared<Bus>(uri, name);
  } catch (...) {
    emit_user_error("passive subscriber construction failed");
    witness.close_sink();
    return 1;
  }

  PinnedBusSubscriber subscriber(bus, &witness);
  witness.emit_state_transition("connected");
  try {
    subscriber.start();
  } catch (...) {
    emit_user_error("passive subscribe registration failed");
    witness.emit_state_transition("disconnected");
    witness.close_sink();
    return 1;
  }

  // Wait for termination. We do not transmit anything.
  while (!g_stop_requested) {
    if (!subscriber.is_connected()) {
      witness.emit_state_transition("disconnected");
      break;
    }
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = 100000000L;  // 100 ms poll
    nanosleep(&ts, nullptr);
  }

  if (g_stop_requested) {
    witness.emit_state_transition("disconnected");
  }
  witness.close_sink();
  return 0;
}

}  // namespace

// ---------------------------------------------------------------------------
// Entry point.
// ---------------------------------------------------------------------------

int main(int argc, char **argv) {
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "--self-test") {
      return run_self_test();
    }
    if (arg == "--help" || arg == "-h") {
      std::cout
          << "passive_nos_engine_time_witness: passive NOS Engine time-witness\n"
          << "  --self-test   Run the deterministic built-in self-test\n"
          << "  <evidence_path> <uri> [name]  Subscribe passively (live)\n";
      return 0;
    }
  }

  // No --self-test: live passive subscribe. The runtime gate is closed.
  return run_live(argc, argv);
}
