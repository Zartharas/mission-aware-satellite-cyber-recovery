# Third-Party Notices and Research Infrastructure

This repository is an independent research project. It references and, in local reproducibility workflows, obtains third-party software that remains governed by its own upstream terms.

## NASA Operational Simulator for Space Systems (NOS3)

- upstream repository: <https://github.com/nasa/nos3>
- pinned research commit: `5a3bdee6be9a2c67fdf994ae6db56d5c60395302`
- frozen description recorded by the project: `v1_07_03-331-g5a3bdee6`
- research toolchain record identifies the upstream license as NASA Open Source Agreement 1.3

The project's `scripts/prepare_nos3_candidate.sh` obtains NOS3 into the ignored local `external/nos3/` directory. NOS3 itself is not relicensed by this repository.

## NASA cFS / cFE-related components selected through NOS3

The frozen NOS3 recursive-submodule inventory selects the cFS/cFE-related component revisions used by the study, including:

- cFE commit: `87e273743f3d07ed9216462b461e9f398ff96c87`
- OSAL commit: `08a79bb6ac02b9ced8aa555853ecdd96e5ebc1a7`
- PSP commit: `d0a5d6fa4093d473a929fde42a0983e489d89d4a`

The project toolchain record notes the public cFS bundle's Apache-2.0 licensing while also requiring each NOS3-pinned submodule to be treated according to its own upstream record.

## Fortytwo / 42

- upstream repository: <https://github.com/nasa-itc/42>
- pinned research commit: `eda252bf31f27850e867e698cfdd963e143ead1f`
- frozen description: `V20260401`

The repository's preparation script obtains this project into the ignored local `external/fortytwo/` directory. Consult the upstream repository for the authoritative license and notices.

## Container image

The frozen research environment used the NOS3 container image identified by:

```text
ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2
```

Container contents remain subject to the licenses of the software included in that image. The image is not relicensed by this repository.

## Python dependencies

Development/test dependencies are listed in [`requirements-dev.txt`](requirements-dev.txt). Each package remains under its own upstream license.

## External publications, standards, and bibliographic records

The repository cites research papers, standards, frameworks, and public technical documentation. Their inclusion as references does not transfer copyright or create a new license grant for the underlying works.

## Names and trademarks

NASA, NOS3, cFS, Fortytwo/42, Docker, GitHub, Zenodo, and other names/logos may be trademarks or identifiers of their respective owners. Their use here is solely descriptive.

## No endorsement

No reference to an upstream project, organization, software package, or archive should be interpreted as sponsorship, certification, approval, or endorsement of this independent research.

For the exact frozen dependency identities, see [`configs/toolchain-lock.json`](configs/toolchain-lock.json), [`artifacts/nos3-submodule-lock.txt`](artifacts/nos3-submodule-lock.txt), and [`artifacts/fortytwo-lock.txt`](artifacts/fortytwo-lock.txt).
