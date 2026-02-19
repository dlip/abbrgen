{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/c5dd43934613ae0f8ff37c59f61c507c2e8f980d";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };
  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python39
          ];
          shellHook = ''
            if [ ! -d "./.venv" ]; then
            	python3 -m venv .venv
            fi
            source .venv/bin/activate
          '';
        };
      }
    );
}
