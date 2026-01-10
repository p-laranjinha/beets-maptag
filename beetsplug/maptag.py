from beets.library import Item
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
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
    # Seeting command outside of commands() so I can print help inside _command().
    command = Subcommand("maptag", help="map metadata fields to file tags")

    def commands(self):
        self.command.parser.usage = "beet maptag [options] query"
        self.command.parser.description = (
            "Map (copy the contents of) metadata fields to file tags."
        )
        self.command.parser.add_option(
            "-m",
            "--map",
            action="append",
            nargs=2,
            help="map a metadata field to a file tag",
            metavar="METADATA_FIELD FILE_TAG",
        )
        self.command.parser.add_option(
            "-s",
            "--skip",
            action="store_true",
            help="skip mapping any track without all the defined metadata fields (if not set, the fields that do exist are applied)",
        )
        self.command.parser.add_option(
            "-d",
            "--delete",
            action="append",
            help="delete a file tag",
            metavar="FILE_TAG",
        )
        self.command.parser.add_option(
            "--delete-field",
            action="append",
            help="delete the file tags associated with a metadata field",
            metavar="METADATA_FIELD",
        )
        self.command.parser.add_option(
            "-q",
            "--quiet",
            action="store_true",
            help="no warning messages",
        )
        self.command.parser.add_option(
            "--quiet_mapping",
            action="store_true",
            help="no warning messages during mapping",
        )
        self.command.parser.add_album_option()
        self.command.func = self._command
        return [self.command]

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
            skip_mapping = False

            if not opts.map and not opts.delete and not opts.delete_field:
                self.command.parser.print_help()
                return

            if opts.map:
                for i in range(len(opts.map)):
                    tmpfieldname = create_tmp_field_name(file, i)
                    if opts.map[i][METADATA_VALUE] not in item:
                        if not opts.quiet and not opts.quiet_mapping:
                            print(
                                f"'{opts.map[i][METADATA_VALUE]}' not found in {file.path}"
                            )
                        if file.path not in missing_field_item_paths:
                            missing_field_item_paths.append(file.path)
                        if opts.skip:
                            skip_mapping = True
                            break
                        else:
                            continue
                    field = create_field(
                        opts.map[i][FILE_TAG],
                        isinstance(item[opts.map[i][METADATA_VALUE]], list),
                    )
                    file.add_field(tmpfieldname, field)
                    try:
                        # This will fail if the format is wrong for already existing
                        #  tags, for example, setting 'year' to a string.
                        setattr(
                            file,
                            tmpfieldname,
                            item[opts.map[i][METADATA_VALUE]],
                        )
                    except Exception as e:
                        exception = e
                        exception_item_path = item.path
                        break
                if exception != None:
                    break
                if skip_mapping:
                    continue
                file.save()

            if opts.delete:
                for i in range(len(opts.delete)):
                    tmpfieldname = create_tmp_field_name(
                        file, (len(opts.map) if opts.map else 0) + i
                    )
                    field = create_field(opts.delete[i])
                    file.add_field(tmpfieldname, field)
                    try:
                        delattr(file, tmpfieldname)
                    except Exception as e:
                        exception = e
                        exception_item_path = item.path
                        break
                if exception != None:
                    break
                file.save()

            if opts.delete_field:
                for field in opts.delete_field:
                    try:
                        delattr(file, field)
                    except Exception as e:
                        exception = e
                        exception_item_path = item.path
                        break
                if exception != None:
                    break
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


def create_tmp_field_name(file: MediaFile, i: int) -> str:
    # Temporary field name that isn't already set here:
    #  https://github.com/beetbox/mediafile/blob/1a41bda1b6863e9145f7d2e74da4a98cb0ffa6fd/mediafile/__init__.py#L373-L861
    #  or by plugins that extend MediaFile.
    # The name itself doesn't matter because we're not permanently adding it to
    #  the database.
    name = f"maptagtmp{i}"
    while name in file.fields():
        name += "a"
    return name


def create_field(tag: str, is_list: bool = False) -> MediaField | ListMediaField:
    # https://github.com/beetbox/beets/blob/ad2ff1f97e686fa2c392355beb0cc16390dcf972/test/plugins/test_plugin_mediafield.py#L29-L41
    # Not sure what all these storage files are for, although I think they
    #  describe different formats.
    if is_list:
        field = ListMediaField(
            MP3ListDescStorageStyle(tag),
            MP4ListStorageStyle(f"----:com.apple.iTunes:{tag}"),
            ListStorageStyle(tag),
            ASFStorageStyle(tag),
        )
    else:
        field = MediaField(
            MP3DescStorageStyle(tag),
            MP4StorageStyle(f"----:com.apple.iTunes:{tag}"),
            StorageStyle(tag),
            ASFStorageStyle(tag),
        )
    return field
