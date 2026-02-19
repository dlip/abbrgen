{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixpkgs-unstable";
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
            python311
            uv
          ];
          shellHook = ''
            export UV_PYTHON=${pkgs.python311}/bin/python
            if [ ! -d "./.venv" ]; then
            	uv venv
            fi
            source .venv/bin/activate
          '';
        };
      }
    );
}
