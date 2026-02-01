"""Result file handling utilities."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import zipfile


class ResultFile:
    """Represents a pipeline result file.

    Provides utilities for packaging and describing result files.
    """

    def __init__(
        self,
        path: Union[str, Path],
        description: str = "",
        category: str = "output",
    ):
        """Initialize a result file.

        Args:
            path: Path to the file.
            description: Human-readable description.
            category: Category for grouping (output, log, intermediate).
        """
        self.path = Path(path)
        self.description = description
        self.category = category

    @property
    def exists(self) -> bool:
        """Check if the file exists."""
        return self.path.exists()

    @property
    def size_bytes(self) -> int:
        """Get file size in bytes."""
        return self.path.stat().st_size if self.exists else 0

    @property
    def size_human(self) -> str:
        """Get human-readable file size."""
        size = self.size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "name": self.path.name,
            "description": self.description,
            "category": self.category,
            "exists": self.exists,
            "size": self.size_human,
        }


class ResultBundle:
    """Collection of result files that can be packaged together.

    Example:
        bundle = ResultBundle("my_analysis")
        bundle.add_file("output.txt", description="Main output")
        bundle.add_file("log.txt", category="log")
        bundle.add_directory("plots/", description="Generated plots")

        zip_path = bundle.create_zip()
    """

    def __init__(self, name: str, base_dir: Optional[Path] = None):
        """Initialize a result bundle.

        Args:
            name: Bundle name (used for zip filename).
            base_dir: Base directory for relative paths.
        """
        self.name = name
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.files: List[ResultFile] = []
        self.directories: List[Path] = []

    def add_file(
        self,
        path: Union[str, Path],
        description: str = "",
        category: str = "output",
    ) -> "ResultBundle":
        """Add a file to the bundle.

        Args:
            path: Path to the file (relative to base_dir or absolute).
            description: Human-readable description.
            category: Category for grouping.

        Returns:
            Self for chaining.
        """
        full_path = self.base_dir / path if not Path(path).is_absolute() else Path(path)
        self.files.append(ResultFile(full_path, description, category))
        return self

    def add_directory(
        self,
        path: Union[str, Path],
        description: str = "",
        pattern: str = "*",
    ) -> "ResultBundle":
        """Add all files from a directory to the bundle.

        Args:
            path: Path to the directory.
            description: Description for files.
            pattern: Glob pattern to filter files.

        Returns:
            Self for chaining.
        """
        dir_path = self.base_dir / path if not Path(path).is_absolute() else Path(path)
        if dir_path.exists() and dir_path.is_dir():
            self.directories.append(dir_path)
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    self.files.append(ResultFile(file_path, description, "output"))
        return self

    def create_zip(
        self,
        output_path: Optional[Path] = None,
        include_empty: bool = False,
    ) -> Optional[Path]:
        """Create a zip file containing all results.

        Args:
            output_path: Path for the zip file. Defaults to {name}_results.zip.
            include_empty: If False, skip files that don't exist.

        Returns:
            Path to the created zip file, or None if no files.
        """
        if output_path is None:
            output_path = self.base_dir / f"{self.name}_results.zip"

        files_to_zip = [f for f in self.files if f.exists or include_empty]

        if not files_to_zip:
            return None

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for result_file in files_to_zip:
                if result_file.exists:
                    # Use relative path in zip
                    try:
                        arc_name = result_file.path.relative_to(self.base_dir)
                    except ValueError:
                        arc_name = result_file.path.name
                    zf.write(result_file.path, arc_name)

        return output_path

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the bundle.

        Returns:
            Dictionary with file counts and total size.
        """
        existing = [f for f in self.files if f.exists]
        total_size = sum(f.size_bytes for f in existing)

        return {
            "name": self.name,
            "file_count": len(existing),
            "total_size": self._format_size(total_size),
            "categories": self._count_by_category(),
            "files": [f.to_dict() for f in existing],
        }

    def _count_by_category(self) -> Dict[str, int]:
        """Count files by category."""
        counts: Dict[str, int] = {}
        for f in self.files:
            if f.exists:
                counts[f.category] = counts.get(f.category, 0) + 1
        return counts

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
