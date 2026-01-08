from beets.library import Item
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
import mediafile
from mediafile import (
    ASFStorageStyle,
    ListMediaField,
    MP3DescStorageStyle,
    MP3ListDescStorageStyle,
    MP4ListStorageStyle,
    MP4StorageStyle,
    MediaField,
    MediaFile,
    StorageStyle,
    ListStorageStyle,
)

METADATA_VALUE = 0
FILE_TAG = 1


class MapTagPlugin(BeetsPlugin):
    def commands(self):
        command = Subcommand("maptag", help="map metadata fields to file tags")
        command.parser.usage = "beet maptag [options] query"
        command.parser.add_option(
            "-i",
            "--input",
            action="append",
            nargs=2,
            help="the metadata field to map from and the file tag it maps to",
            metavar="METADATA_FIELD FILE_TAG",
        )
        command.parser.add_option(
            "-s",
            "--skip",
            action="store_true",
            help="skip any track without all the defined metadata fields (if not set, the fields that do exist are applied)",
        )
        command.parser.add_option(
            "-q",
            "--quiet",
            action="store_true",
            help="no warning messages",
        )
        command.parser.add_option(
            "-e",
            "--quiet_execution",
            action="store_true",
            help="no warning messages during execution",
        )
        command.parser.add_album_option()
        command.func = self._command
        return [command]

    def _command(self, lib, opts, args):
        if opts.album:
            items: list[Item] = [album.items() for album in lib.albums(args)]
        else:
            items: list[Item] = lib.items(args)

        missing_field_item_paths = []
        exception = None
        exception_item_path = None
        for item in items:
            file = MediaFile(item.path)
            skip_file = False
            for i in range(len(opts.input)):
                # Temporary field name that isn't already set here:
                #  https://github.com/beetbox/mediafile/blob/1a41bda1b6863e9145f7d2e74da4a98cb0ffa6fd/mediafile/__init__.py#L373-L861
                #  or by plugins that extend MediaFile.
                # The name itself doesn't matter because we're not permanently
                #  adding it to the database.
                tmpfieldname = f"maptagtmp{i}"
                while tmpfieldname in file.fields():
                    tmpfieldname += "a"

                if opts.input[i][METADATA_VALUE] not in item:
                    if not opts.quiet and not opts.quiet_execution:
                        print(
                            f"'{opts.input[i][METADATA_VALUE]}' not found in {file.path}"
                        )
                    if file.path not in missing_field_item_paths:
                        missing_field_item_paths.append(file.path)
                    if opts.skip:
                        skip_file = True
                        break
                    else:
                        continue

                # https://github.com/beetbox/beets/blob/ad2ff1f97e686fa2c392355beb0cc16390dcf972/test/plugins/test_plugin_mediafield.py#L29-L41
                # Not sure what all these storage files are for, although I
                #  think they describe different formats.
                if isinstance(item[opts.input[i][METADATA_VALUE]], list):
                    field = ListMediaField(
                        MP3ListDescStorageStyle(opts.input[i][FILE_TAG]),
                        MP4ListStorageStyle(
                            f"----:com.apple.iTunes:{opts.input[i][FILE_TAG]}"
                        ),
                        ListStorageStyle(opts.input[i][FILE_TAG]),
                        ASFStorageStyle(opts.input[i][FILE_TAG]),
                    )
                else:
                    field = MediaField(
                        MP3DescStorageStyle(opts.input[i][FILE_TAG]),
                        MP4StorageStyle(
                            f"----:com.apple.iTunes:{opts.input[i][FILE_TAG]}"
                        ),
                        StorageStyle(opts.input[i][FILE_TAG]),
                        ASFStorageStyle(opts.input[i][FILE_TAG]),
                    )
                file.add_field(tmpfieldname, field)

                try:
                    # This will fail if the format is wrong for already existing
                    #  tags, for example, setting 'year' to a string.
                    setattr(
                        file,
                        tmpfieldname,
                        item[opts.input[i][METADATA_VALUE]],
                    )
                except Exception as e:
                    exception = e
                    exception_item_path = item.path
                    break

            if exception != None:
                break
            if skip_file:
                continue
            file.save()

        if len(missing_field_item_paths) > 0 and not opts.quiet:
            print("Files with missing metadata fields:")
            for path in missing_field_item_paths:
                print(path)

        if exception != None:
            print(
                f"Execution stopped on the {exception_item_path} file due to the following error:"
            )
            raise exception
