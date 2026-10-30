import subprocess
import sys
from pathlib import Path


def test_metadata_install_handles_filetypes_named_package_json(tmp_path):
    source=tmp_path/'source';target=tmp_path/'target'
    relative=Path('filetypes/package.json')
    (source/relative).mkdir(parents=True);(target/relative).mkdir(parents=True)
    (source/relative/'accepted_config.json').write_text('{"current":true}')
    (target/relative/'model.onnx').write_bytes(b'unchanged')
    subprocess.run([sys.executable,str(Path(__file__).parents[1]/'scripts/install_azoth_config_metadata.py'),str(source),str(target)],check=True)
    assert (target/relative/'accepted_config.json').read_text()=='{"current":true}'
    assert (target/relative/'model.onnx').read_bytes()==b'unchanged'
