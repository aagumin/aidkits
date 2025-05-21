import json
import os
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


class JsonSplitter:
    """
    A utility class for splitting a large JSON file into multiple smaller files based on a grouping field.

    This class reads a JSON file containing a list of dictionaries, groups them by a specified field,
    and saves each group to a separate JSON file.
    """

    def __init__(self, output_dir: str = 'output_by_title'):
        """
        Initialize the JsonSplitter with the specified output directory.

        Args:
            output_dir: The directory where the split JSON files will be saved.
                        Default is 'output_by_title'.
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

    def _create_output_directory(self) -> None:
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Create a safe filename by replacing invalid characters.

        Args:
            filename: The original filename that may contain invalid characters.

        Returns:
            A sanitized filename safe for file system operations.
        """
        # Replace common invalid characters
        safe_filename = filename.replace('/', '_').replace('\\', '_')
        safe_filename = safe_filename.replace(':', '_').replace('*', '_')
        safe_filename = safe_filename.replace('?', '_').replace('"', '_')
        safe_filename = safe_filename.replace('<', '_').replace('>', '_')
        safe_filename = safe_filename.replace('|', '_')

        # Ensure the filename ends with .json
        if not safe_filename.endswith('.json'):
            safe_filename += '.json'

        return safe_filename

    def split_json_file(
        self, 
        input_file: Union[str, Path], 
        group_by_field: str = 'title',
        encoding: str = 'utf-8'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Split a JSON file into multiple files based on a grouping field.

        Args:
            input_file: Path to the input JSON file.
            group_by_field: The field to group the data by. Default is 'title'.
            encoding: The encoding of the input file. Default is 'utf-8'.

        Returns:
            A dictionary mapping group names to lists of items in that group.

        Raises:
            FileNotFoundError: If the input file doesn't exist.
            json.JSONDecodeError: If the input file is not valid JSON.
            KeyError: If an item doesn't have the specified group_by_field.
        """
        try:
            # Ensure input_file is a string
            input_file_str = str(input_file)

            # Read the JSON file
            self.logger.info(f"Reading JSON file: {input_file_str}")
            with open(input_file_str, 'r', encoding=encoding) as file:
                data = json.load(file)

            # Create the output directory
            self._create_output_directory()

            # Group the data by the specified field
            grouped_data: Dict[str, List[Dict[str, Any]]] = {}
            for item in data:
                if group_by_field in item:
                    group_value = item[group_by_field]
                    if group_value not in grouped_data:
                        grouped_data[group_value] = []
                    grouped_data[group_value].append(item)
                else:
                    self.logger.warning(f"Item missing '{group_by_field}' field: {item}")

            # Save each group to a separate file
            for group_name, items in grouped_data.items():
                safe_filename = self._sanitize_filename(group_name)
                output_path = os.path.join(self.output_dir, safe_filename)

                with open(output_path, 'w', encoding=encoding) as out_file:
                    json.dump(items, out_file, ensure_ascii=False, indent=4)

                self.logger.info(f"Saved file: {output_path} ({len(items)} items)")

            self.logger.info(f"Total files created: {len(grouped_data)}")
            return grouped_data

        except FileNotFoundError:
            self.logger.error(f"Input file not found: {input_file_str}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in file: {input_file_str}")
            raise
        except Exception as e:
            self.logger.error(f"Error splitting JSON file: {str(e)}")
            raise

    def split_json_data(
        self, 
        data: List[Dict[str, Any]], 
        group_by_field: str = 'title',
        encoding: str = 'utf-8'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Split JSON data into multiple files based on a grouping field.

        Args:
            data: The JSON data as a list of dictionaries.
            group_by_field: The field to group the data by. Default is 'title'.
            encoding: The encoding to use for the output files. Default is 'utf-8'.

        Returns:
            A dictionary mapping group names to lists of items in that group.

        Raises:
            KeyError: If an item doesn't have the specified group_by_field.
        """
        try:
            # Create the output directory
            self._create_output_directory()

            # Group the data by the specified field
            grouped_data: Dict[str, List[Dict[str, Any]]] = {}
            for item in data:
                if group_by_field in item:
                    group_value = item[group_by_field]
                    if group_value not in grouped_data:
                        grouped_data[group_value] = []
                    grouped_data[group_value].append(item)
                else:
                    self.logger.warning(f"Item missing '{group_by_field}' field: {item}")

            # Save each group to a separate file
            for group_name, items in grouped_data.items():
                safe_filename = self._sanitize_filename(group_name)
                output_path = os.path.join(self.output_dir, safe_filename)

                with open(output_path, 'w', encoding=encoding) as out_file:
                    json.dump(items, out_file, ensure_ascii=False, indent=4)

                self.logger.info(f"Saved file: {output_path} ({len(items)} items)")

            self.logger.info(f"Total files created: {len(grouped_data)}")
            return grouped_data

        except Exception as e:
            self.logger.error(f"Error splitting JSON data: {str(e)}")
            raise


def main():
    """Command-line interface for the JsonSplitter class."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Split a JSON file into multiple files based on a grouping field.'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the input JSON file.'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output_by_title',
        help='Directory where the split JSON files will be saved. Default is "output_by_title".'
    )
    parser.add_argument(
        '--group-by',
        type=str,
        default='title',
        help='Field to group the data by. Default is "title".'
    )
    parser.add_argument(
        '--encoding',
        type=str,
        default='utf-8',
        help='Encoding of the input file. Default is "utf-8".'
    )

    args = parser.parse_args()

    # Create a JsonSplitter instance and split the file
    splitter = JsonSplitter(output_dir=args.output_dir)
    try:
        grouped_data = splitter.split_json_file(
            input_file=args.input_file,
            group_by_field=args.group_by,
            encoding=args.encoding
        )
        print(f"\nTotal files created: {len(grouped_data)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
