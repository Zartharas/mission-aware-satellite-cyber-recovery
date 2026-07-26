# WP4 Radio Queue and Time Callback Audit Plan

Date: 2026-07-26

## Accepted retained transport observation

Retained run `20260726T192902Z` recorded 1,061 successful `recvfrom` calls on generic-radio UDP `5011` and no successful or failed `sendto` calls to UDP `8011`. The retained evidence audit, component snapshots, evidence hashes, zero-command controls, and cleanup checks passed.

This transport observation remains valid and is separate from any claim about NOS Engine time progression, callback delivery, or callback queue visibility.

## Source-supported queue path

The retained generic-radio configuration uses:

- `downlink-close-criteria=none`
- `downlink-delay-on=false`
- FSW telemetry input UDP `5011`
- ground telemetry destination UDP `8011`

At generic-radio commit `a2effa73715ab4fe2fdc41e549ae2dca81214d98`, the `none` criterion makes downlink communication capable and the disabled delay leaves delay at zero. A successful receive should then create a downlink queue entry. The queue is released only by `process_forward_loop_message_queue`, which is registered as a NOS Engine time-tick callback.

## D-056 parser correction

The first read-only callback audit used the broad expression `tick\s*=\s*(\d+)`. On the retained time-log line containing both `TimeDriver::send_tick_to_nos_engine:tick = 0` and `real microseconds per tick = 10000`, that expression incorrectly treated `10000` as a second time tick.

The authoritative parser is now scoped to `TimeDriver::send_tick_to_nos_engine:tick\s*=\s*(\d+)` and accepts at most one authoritative tick value per log line. The retained log therefore contains one authoritative tick value, `0`, rather than two advancing tick values.

## Corrected interpretation

- `time_tick_marker_count=1`
- `time_tick_distinct_values=1`
- `time_tick_min=0`
- `time_tick_max=0`
- `retained_time_progress_proven=0`
- `read_only_diagnosis=RADIO_TIME_PROGRESS_OR_CALLBACK_INVOCATION_UNPROVEN_BY_RETAINED_LOG`

The retained evidence proves UDP `5011` ingress and absence of any UDP `8011` send attempt. It does not prove advancing NOS Engine time, callback invocation after ingress, or queue visibility inside the callback.

## Control state

- Diagnostic runtime authorization: closed
- Authorized runtime attempts: zero
- Baseline execution: blocked
- Event injection: blocked
- Scientific outcome classification: blocked
- CryptoLib/SDLS interpretation: separate and blocked

## Validation boundary

Only bash syntax validation, the parser regression self-test, and the corrected read-only auditor against retained run `20260726T192902Z` are authorized. Do not rerun the diagnostic, Docker, NOS3, any simulator, a baseline, or an event-injection path.
