# main_script.spec

# Example spec file
block_cipher = None

added_files = [
    ('pokemon_details.json', '.'),   # Include JSON files
    ('abilities.json', '.'),
    ('settings.json', '.'),
    ('font/pokemon-emerald-pro.otf', 'font'),  # Include fonts in 'font' subdirectory
    ('sprites/*.png', 'sprites'),   # Include all PNG files in 'sprites' directory
    ('types/*.png', 'types'),
    ('design.ui', '.')  # Include design.ui in the root directory
]

a = Analysis(['main.py'],
             pathex=['/home/flora/Projects/Pokedex'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='QDex',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          onefile=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main_script')

