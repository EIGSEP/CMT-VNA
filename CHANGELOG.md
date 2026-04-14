# Changelog

## [1.0.0](https://github.com/EIGSEP/CMT-VNA/compare/v0.0.2...v1.0.0) (2026-04-14)


### ⚠ BREAKING CHANGES

* `VNA.__init__` parameter renamed `switch_network` -> `switch_fn`, and `VNA.switch_nw` attribute renamed `VNA.switch_fn`. Pass a callable (e.g. `snw.switch` or a lambda) rather than a switch network object.

### Code Refactoring

* replace switch_network object with switch_fn callable ([c65f09f](https://github.com/EIGSEP/CMT-VNA/commit/c65f09f546317f79208c718e34527dd4f0307b9a))

## [0.0.2](https://github.com/EIGSEP/CMT-VNA/compare/v0.0.1...v0.0.2) (2026-03-25)


### Bug Fixes

* numpy array truthiness in S911T.sparams ([#22](https://github.com/EIGSEP/CMT-VNA/issues/22)) ([60561a5](https://github.com/EIGSEP/CMT-VNA/commit/60561a53b93fe0a81edc0b75a4af7f776e77d37e))
