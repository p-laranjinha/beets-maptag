# beets-maptag

Beets plugin to map (copy the contents of) metadata fields to file tags.

```
Usage: beet maptag [options] query

Map (copy the contents of) metadata fields to file tags.

Options:
  -h, --help            show this help message and exit
  -m METADATA_FIELD FILE_TAG, --map=METADATA_FIELD FILE_TAG
                        map a metadata field to a file tag
  -s, --skip            skip mapping any track without all the defined
                        metadata fields (if not set, the fields that do exist
                        are applied)
  -d FILE_TAG, --delete=FILE_TAG
                        delete a file tag
  --delete-field=METADATA_FIELD
                        delete the file tags associated with a metadata field
  -q, --quiet           no warning messages
  --quiet_mapping       no warning messages during mapping
  -a, --album           match albums instead of tracks
```

Example usage:
```
# Map the metadata value 'year' to the tag 'date' on all tracks
beet maptag -m year date

# Add the 'mood_happy' and 'mood_sad' tags to all tracks made by the artist 'mili'
beet maptag -m mood_happy mood_happy -m mood_sad mood_sad artist:mili

# Delete the 'comment' and 'description' tags from all tracks
beet maptag -d comment -d description

# MP3 files are harder to generalize so to delete normal beets tags on MP3s use this
# Delete all tags associated with the 'catalognums' metadata field
beet maptage --delete-field catalognums
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
                version = "master";
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
