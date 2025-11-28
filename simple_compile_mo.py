#!/usr/bin/env python
"""
Simple .mo file compiler using struct
Creates binary .mo files from .po files without requiring gettext
"""
import struct
import array
from pathlib import Path

def parse_po_file(po_path):
    """Parse a .po file and return msgid/msgstr pairs"""
    translations = {}
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False
    
    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Start of msgid
            if line.startswith('msgid '):
                if current_msgid is not None and current_msgstr is not None:
                    translations[current_msgid] = current_msgstr
                current_msgid = line[7:-1]  # Remove 'msgid "' and '"'
                in_msgid = True
                in_msgstr = False
                continue
            
            # Start of msgstr
            if line.startswith('msgstr '):
                current_msgstr = line[8:-1]  # Remove 'msgstr "' and '"'
                in_msgid = False
                in_msgstr = True
                continue
            
            # Continuation line
            if line.startswith('"') and line.endswith('"'):
                text = line[1:-1]
                if in_msgid:
                    current_msgid += text
                elif in_msgstr:
                    current_msgstr += text
        
        # Add last entry
        if current_msgid is not None and current_msgstr is not None:
            translations[current_msgid] = current_msgstr
    
    return translations

def generate_mo_file(translations, mo_path):
    """Generate a .mo file from translations dictionary"""
    # Filter out empty translations
    translations = {k: v for k, v in translations.items() if k and v}
    
    # Sort by msgid
    keys = sorted(translations.keys())
    offsets = []
    ids = []
    strs = []
    
    for key in keys:
        ids.append(key.encode('utf-8'))
        strs.append(translations[key].encode('utf-8'))
    
    # Calculate offsets
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + sum(len(k) + 1 for k in ids)
    
    koffsets = []
    voffsets = []
    
    # Calculate key offsets
    offset = keystart
    for k in ids:
        koffsets.append((len(k), offset))
        offset += len(k) + 1
    
    # Calculate value offsets
    offset = valuestart
    for v in strs:
        voffsets.append((len(v), offset))
        offset += len(v) + 1
    
    # Generate .mo file
    with open(mo_path, 'wb') as f:
        # Magic number
        f.write(struct.pack('I', 0x950412de))
        # Version
        f.write(struct.pack('I', 0))
        # Number of entries
        f.write(struct.pack('I', len(keys)))
        # Offset of table with original strings
        f.write(struct.pack('I', 7 * 4))
        # Offset of table with translation strings
        f.write(struct.pack('I', 7 * 4 + len(keys) * 8))
        # Size of hashing table
        f.write(struct.pack('I', 0))
        # Offset of hashing table
        f.write(struct.pack('I', 0))
        
        # Write key offsets
        for length, offset in koffsets:
            f.write(struct.pack('I', length))
            f.write(struct.pack('I', offset))
        
        # Write value offsets
        for length, offset in voffsets:
            f.write(struct.pack('I', length))
            f.write(struct.pack('I', offset))
        
        # Write keys
        for k in ids:
            f.write(k)
            f.write(b'\x00')
        
        # Write values
        for v in strs:
            f.write(v)
            f.write(b'\x00')

def main():
    """Compile all .po files to .mo files"""
    print("Compiling translation files...")
    print()
    
    locale_dir = Path('locale')
    po_files = list(locale_dir.glob('**/*.po'))
    
    if not po_files:
        print("✗ No .po files found")
        return 1
    
    success = 0
    for po_file in po_files:
        try:
            mo_file = po_file.with_suffix('.mo')
            translations = parse_po_file(po_file)
            generate_mo_file(translations, mo_file)
            print(f"✓ Compiled: {po_file} -> {mo_file}")
            success += 1
        except Exception as e:
            print(f"✗ Failed to compile {po_file}: {e}")
    
    print()
    print(f"Successfully compiled {success}/{len(po_files)} file(s)")
    return 0 if success == len(po_files) else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
