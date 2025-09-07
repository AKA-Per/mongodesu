# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-09-06
### Added
- Support for ```generics``` typing for type hinting
- Added return of model instance itself when calling the ```save``` method.
- Added support for return of the Model instance from the ```find_one``` and ```find``` method.

### Changed
- Converted all the model function to classmethod to directly invoked through the ```Model``` class.

### Fixed
- Bug in ```save()``` method when calling on existing record creates duplicate entry.


## [2.0.0] - 2.25-09-07
### Fixed
- Major Bug Fix - Serialization imports error fixed.

### Major Chamged
- Imports for ```types```, ```Model```, changed for end user.
- All imports are converted to module import with ```__init__```
