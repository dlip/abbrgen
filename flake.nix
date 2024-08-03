{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };
  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python39
            libmysqlclient
            pkg-config
            libffi
          ];
          shellHook = ''
            if [ ! -d "./venv "]; then
            	python3 -m venv venv
            fi
            source venv/bin/activate
          '';
        };
      }
    );
}
