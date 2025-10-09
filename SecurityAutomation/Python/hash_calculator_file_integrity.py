#!/usr/bin/env python3
"""
Hash Calculator & File Integrity Checker
A utility script for calculating file hashes, verifying integrity, and generating hash manifests.
"""

import hashlib
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class HashCalculator:
    """Calculate and verify cryptographic hashes for files and strings."""
    
    SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha384', 'sha512', 'sha3_256', 'sha3_512']
    CHUNK_SIZE = 8192  # Read files in 8KB chunks
    
    def __init__(self, algorithms: List[str] = None):
        """
        Initialize the hash calculator.
        
        Args:
            algorithms: List of hash algorithms to use. Defaults to common ones.
        """
        if algorithms is None:
            self.algorithms = ['md5', 'sha1', 'sha256']
        else:
            # Validate algorithms
            invalid = [a for a in algorithms if a not in self.SUPPORTED_ALGORITHMS]
            if invalid:
                raise ValueError(f"Unsupported algorithms: {', '.join(invalid)}")
            self.algorithms = algorithms
    
    def hash_string(self, text: str) -> Dict[str, str]:
        """
        Calculate hashes for a string.
        
        Args:
            text: The text to hash
            
        Returns:
            Dictionary mapping algorithm names to hash values
        """
        hashes = {}
        data = text.encode('utf-8')
        
        for algo in self.algorithms:
            h = hashlib.new(algo)
            h.update(data)
            hashes[algo] = h.hexdigest()
        
        return hashes
    
    def hash_file(self, filepath: str, show_progress: bool = False) -> Dict[str, str]:
        """
        Calculate hashes for a file.
        
        Args:
            filepath: Path to the file
            show_progress: Display progress for large files
            
        Returns:
            Dictionary mapping algorithm names to hash values
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not os.path.isfile(filepath):
            raise ValueError(f"Not a file: {filepath}")
        
        # Initialize hash objects
        hash_objects = {algo: hashlib.new(algo) for algo in self.algorithms}
        
        file_size = os.path.getsize(filepath)
        bytes_read = 0
        
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    for h in hash_objects.values():
                        h.update(chunk)
                    
                    if show_progress and file_size > 1024 * 1024:  # Show for files > 1MB
                        bytes_read += len(chunk)
                        progress = (bytes_read / file_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='', file=sys.stderr)
            
            if show_progress and file_size > 1024 * 1024:
                print("\r", end='', file=sys.stderr)  # Clear progress line
            
            return {algo: h.hexdigest() for algo, h in hash_objects.items()}
        
        except Exception as e:
            raise RuntimeError(f"Error reading file {filepath}: {e}")
    
    def verify_file(self, filepath: str, expected_hash: str, algorithm: str = 'sha256') -> Tuple[bool, str]:
        """
        Verify a file against an expected hash.
        
        Args:
            filepath: Path to the file
            expected_hash: The expected hash value
            algorithm: Hash algorithm to use
            
        Returns:
            Tuple of (matches, actual_hash)
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        original_algos = self.algorithms
        self.algorithms = [algorithm]
        
        try:
            actual_hashes = self.hash_file(filepath)
            actual_hash = actual_hashes[algorithm]
            matches = actual_hash.lower() == expected_hash.lower()
            return matches, actual_hash
        finally:
            self.algorithms = original_algos
    
    def generate_manifest(self, directory: str, recursive: bool = True, 
                         extensions: List[str] = None) -> Dict:
        """
        Generate a hash manifest for all files in a directory.
        
        Args:
            directory: Directory path to scan
            recursive: Scan subdirectories
            extensions: Filter by file extensions (e.g., ['.exe', '.dll'])
            
        Returns:
            Dictionary containing manifest data
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Not a directory: {directory}")
        
        manifest = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'base_directory': os.path.abspath(directory),
                'algorithms': self.algorithms,
                'recursive': recursive
            },
            'files': {}
        }
        
        # Collect files
        files_to_hash = []
        if recursive:
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if extensions is None or any(filename.endswith(ext) for ext in extensions):
                        files_to_hash.append(filepath)
        else:
            for item in os.listdir(directory):
                filepath = os.path.join(directory, item)
                if os.path.isfile(filepath):
                    if extensions is None or any(item.endswith(ext) for ext in extensions):
                        files_to_hash.append(filepath)
        
        # Hash files
        total_files = len(files_to_hash)
        for idx, filepath in enumerate(files_to_hash, 1):
            try:
                rel_path = os.path.relpath(filepath, directory)
                print(f"Hashing ({idx}/{total_files}): {rel_path}", file=sys.stderr)
                
                hashes = self.hash_file(filepath)
                file_stat = os.stat(filepath)
                
                manifest['files'][rel_path] = {
                    'hashes': hashes,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                }
            except Exception as e:
                print(f"Error processing {filepath}: {e}", file=sys.stderr)
                manifest['files'][rel_path] = {'error': str(e)}
        
        return manifest
    
    def verify_manifest(self, manifest_path: str, base_directory: str = None) -> Dict:
        """
        Verify files against a manifest.
        
        Args:
            manifest_path: Path to the manifest JSON file
            base_directory: Base directory (overrides manifest metadata)
            
        Returns:
            Dictionary with verification results
        """
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        if base_directory is None:
            base_directory = manifest['metadata'].get('base_directory', '.')
        
        results = {
            'verified_at': datetime.now().isoformat(),
            'total_files': len(manifest['files']),
            'passed': 0,
            'failed': 0,
            'missing': 0,
            'details': {}
        }
        
        for rel_path, file_data in manifest['files'].items():
            filepath = os.path.join(base_directory, rel_path)
            
            if 'error' in file_data:
                results['details'][rel_path] = {'status': 'skipped', 'reason': 'error in manifest'}
                continue
            
            if not os.path.exists(filepath):
                results['missing'] += 1
                results['details'][rel_path] = {'status': 'missing'}
                continue
            
            # Verify hashes
            try:
                current_hashes = self.hash_file(filepath)
                manifest_hashes = file_data['hashes']
                
                mismatches = []
                for algo in manifest_hashes.keys():
                    if algo in current_hashes:
                        if current_hashes[algo] != manifest_hashes[algo]:
                            mismatches.append({
                                'algorithm': algo,
                                'expected': manifest_hashes[algo],
                                'actual': current_hashes[algo]
                            })
                
                if mismatches:
                    results['failed'] += 1
                    results['details'][rel_path] = {
                        'status': 'failed',
                        'mismatches': mismatches
                    }
                else:
                    results['passed'] += 1
                    results['details'][rel_path] = {'status': 'passed'}
            
            except Exception as e:
                results['failed'] += 1
                results['details'][rel_path] = {
                    'status': 'error',
                    'reason': str(e)
                }
        
        return results
    
    def compare_files(self, file1: str, file2: str) -> Dict:
        """
        Compare two files using hashes.
        
        Args:
            file1: Path to first file
            file2: Path to second file
            
        Returns:
            Dictionary with comparison results
        """
        hashes1 = self.hash_file(file1)
        hashes2 = self.hash_file(file2)
        
        result = {
            'file1': file1,
            'file2': file2,
            'identical': all(hashes1[a] == hashes2[a] for a in self.algorithms),
            'hashes': {
                'file1': hashes1,
                'file2': hashes2
            }
        }
        
        return result


def format_hash_output(filepath: str, hashes: Dict[str, str], verbose: bool = False) -> str:
    """Format hash output for display."""
    lines = []
    
    if verbose:
        lines.append(f"\nFile: {filepath}")
        lines.append("-" * 80)
        for algo, hash_value in hashes.items():
            lines.append(f"{algo.upper():10s}: {hash_value}")
    else:
        for algo, hash_value in hashes.items():
            lines.append(f"{hash_value}  {filepath}")
    
    return '\n'.join(lines)


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Calculate and verify cryptographic hashes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hash a single file
  python hash_calculator.py -f malware.exe
  
  # Hash with specific algorithms
  python hash_calculator.py -f file.pdf -a sha256 sha512
  
  # Hash a string
  python hash_calculator.py -s "password123"
  
  # Generate manifest for directory
  python hash_calculator.py -m generate -d ./important_files -o manifest.json
  
  # Verify against manifest
  python hash_calculator.py -m verify -i manifest.json -d ./important_files
  
  # Compare two files
  python hash_calculator.py -c file1.exe file2.exe
  
  # Verify file against known hash
  python hash_calculator.py -f file.iso --verify sha256:abc123def456...
        """
    )
    
    parser.add_argument('-f', '--file', help='Hash a single file')
    parser.add_argument('-s', '--string', help='Hash a string')
    parser.add_argument('-d', '--directory', help='Directory path for manifest operations')
    parser.add_argument('-c', '--compare', nargs=2, metavar=('FILE1', 'FILE2'),
                       help='Compare two files')
    parser.add_argument('-a', '--algorithms', nargs='+', 
                       choices=HashCalculator.SUPPORTED_ALGORITHMS,
                       default=['md5', 'sha1', 'sha256'],
                       help='Hash algorithms to use')
    parser.add_argument('-m', '--manifest', choices=['generate', 'verify'],
                       help='Manifest operation mode')
    parser.add_argument('-i', '--input', help='Input manifest file for verification')
    parser.add_argument('-o', '--output', help='Output file for manifest')
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                       help='Recursive directory scanning (default: True)')
    parser.add_argument('-e', '--extensions', nargs='+',
                       help='File extensions to include (e.g., .exe .dll)')
    parser.add_argument('--verify', metavar='ALGO:HASH',
                       help='Verify file against hash (format: algorithm:hash)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize calculator
    calc = HashCalculator(args.algorithms)
    
    try:
        # String hashing
        if args.string:
            hashes = calc.hash_string(args.string)
            print(format_hash_output("(string)", hashes, args.verbose))
        
        # File hashing
        elif args.file:
            if args.verify:
                # Verify mode
                parts = args.verify.split(':', 1)
                if len(parts) != 2:
                    print("Error: --verify format should be algorithm:hash", file=sys.stderr)
                    sys.exit(1)
                
                algo, expected = parts
                matches, actual = calc.verify_file(args.file, expected, algo)
                
                if matches:
                    print(f"✓ VERIFICATION PASSED")
                    print(f"File: {args.file}")
                    print(f"{algo.upper()}: {actual}")
                    sys.exit(0)
                else:
                    print(f"✗ VERIFICATION FAILED")
                    print(f"File: {args.file}")
                    print(f"Expected {algo.upper()}: {expected}")
                    print(f"Actual {algo.upper()}:   {actual}")
                    sys.exit(1)
            else:
                # Regular hashing
                hashes = calc.hash_file(args.file, show_progress=True)
                print(format_hash_output(args.file, hashes, args.verbose))
        
        # Compare files
        elif args.compare:
            result = calc.compare_files(args.compare[0], args.compare[1])
            
            if result['identical']:
                print("✓ FILES ARE IDENTICAL")
            else:
                print("✗ FILES ARE DIFFERENT")
            
            print(f"\nFile 1: {result['file1']}")
            for algo, hash_val in result['hashes']['file1'].items():
                print(f"  {algo.upper()}: {hash_val}")
            
            print(f"\nFile 2: {result['file2']}")
            for algo, hash_val in result['hashes']['file2'].items():
                print(f"  {algo.upper()}: {hash_val}")
            
            sys.exit(0 if result['identical'] else 1)
        
        # Manifest operations
        elif args.manifest == 'generate':
            if not args.directory:
                print("Error: -d/--directory required for manifest generation", file=sys.stderr)
                sys.exit(1)
            
            manifest = calc.generate_manifest(args.directory, args.recursive, args.extensions)
            
            output_file = args.output or 'hash_manifest.json'
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"\n✓ Manifest generated: {output_file}")
            print(f"  Total files: {len(manifest['files'])}")
            print(f"  Algorithms: {', '.join(manifest['metadata']['algorithms'])}")
        
        elif args.manifest == 'verify':
            if not args.input:
                print("Error: -i/--input required for manifest verification", file=sys.stderr)
                sys.exit(1)
            
            results = calc.verify_manifest(args.input, args.directory)
            
            print("\n" + "=" * 80)
            print("MANIFEST VERIFICATION RESULTS")
            print("=" * 80)
            print(f"Total files: {results['total_files']}")
            print(f"✓ Passed:    {results['passed']}")
            print(f"✗ Failed:    {results['failed']}")
            print(f"? Missing:   {results['missing']}")
            
            if results['failed'] > 0 or results['missing'] > 0:
                print("\nDETAILS:")
                print("-" * 80)
                for filepath, detail in results['details'].items():
                    if detail['status'] in ['failed', 'missing']:
                        print(f"\n{filepath}: {detail['status'].upper()}")
                        if 'mismatches' in detail:
                            for m in detail['mismatches']:
                                print(f"  {m['algorithm'].upper()}:")
                                print(f"    Expected: {m['expected']}")
                                print(f"    Actual:   {m['actual']}")
            
            sys.exit(0 if results['failed'] == 0 and results['missing'] == 0 else 1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()