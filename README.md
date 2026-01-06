# beets-maptag

Beets plugin to map metadata fields to file tags.

```
Usage: beet maptag [options] query

Options:
  -h, --help            show this help message and exit
  -i METADATA_FIELD FILE_TAG, --input=METADATA_FIELD FILE_TAG
                        the metadata field to map from and the file tag it
                        maps to
  -s, --skip            skip any track without all the defined metadata fields
                        (if not set, the fields that do exist are applied)
  -q, --quiet           no warning messages
  -e, --quiet_execution
                        no warning messages during execution
  -a, --album           match albums instead of tracks
```

Example usage:
```
# Map the metadata value 'artist' to the tag 'albumartist' on all tracks
beet maptag -i artist albumartist

# Add the 'mood_happy' and 'mood_sad' tags to all tracks made by the artist 'mili'
beet maptag -i mood_happy mood_happy -i mood_sad mood_sad artist:mili
```

## Installing

I'm don't install this way (because I use NixOS) but the following should work:
```bash
git clone https://github.com/p-laranjinha/beets-maptag.git
cd beets-maptag
python setup.py install
```

Don't forget to add it to the beets config:
```yaml
plugins:
  - maptag
```

### In NixOS

This is probably not the best way to do this, but its the way I do it (changing the hash to the correct one):
```nix
{pkgs, ...}: {
  nixpkgs.overlays = [
    (
      final: prev: {
        pythonPackagesExtensions =
          prev.pythonPackagesExtensions
          ++ [
            (python-final: python-prev: {
              beets-maptag = python-prev.buildPythonPackage {
                pname = "beets-maptag";
                version = "0.0.2";
                pyproject = true;

                src = prev.fetchFromGitHub {
                  owner = "p-laranjinha";
                  repo = "beets-maptag";
                  rev = "master";
                  hash = "";
                };

                build-system = with python-prev; [
                  setuptools
                ];

                nativeBuildInputs = with python-prev; [
                  beets
                ];

                passthru = {
                  updateScript = python-prev.nix-update-script {};
                };
              };
            })
            (python-final: python-prev: {
              beets = python-prev.beets.override {
                pluginOverrides = {
                  maptag = {
                    enable = true;
                    propagatedBuildInputs = [python-prev.beets-maptag];
                  };
                };
              };
            })
          ];
      }
    )
  ];
  environment.systemPackages = [ pkgs.beets ];
}
```
