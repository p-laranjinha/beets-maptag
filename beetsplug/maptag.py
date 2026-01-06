from beets.library import Item
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from mediafile import MP3DescStorageStyle, MediaField, MediaFile, StorageStyle

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

                if opts.input[i][FILE_TAG] not in file.fields():
                    field = MediaField(
                        MP3DescStorageStyle(), StorageStyle(opts.input[i][FILE_TAG])
                    )
                    file.add_field(opts.input[i][FILE_TAG], field)

                try:
                    # This will fail if the format is wrong for already existing
                    #  tags, for example, setting 'year' to a string.
                    setattr(
                        file,
                        opts.input[i][FILE_TAG],
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
