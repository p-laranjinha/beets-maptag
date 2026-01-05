{
  description = "Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = {nixpkgs, ...}: let
    system = "x86_64-linux";
  in {
    devShells.${system} = let
      pkgs = import nixpkgs {inherit system;};
      python3 = pkgs.python313;
      # A set of system dependencies for Python modules.
      # They act as build inputs and are used to configure
      # LD_LIBRARY_PATH in the shell.
      systemPackages = with pkgs; [
      ];
    in {
      default = pkgs.mkShell {
        venvDir = ".venv";

        buildInputs = with python3.pkgs;
          [
            python3
            beets
            setuptools
            venvShellHook
            pip
          ]
          ++ systemPackages;

        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
        '';

        LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath systemPackages}";

        shellHook = ''
        '';

        postShellHook = ''
          unset SOURCE_DATE_EPOCH
        '';
      };
    };
  };
}
