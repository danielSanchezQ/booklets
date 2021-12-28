from pathlib import Path
from typing import Generator, cast
from itertools import chain, repeat
from PyPDF2 import PdfFileReader, PdfFileWriter, PageRange
from PyPDF2.pdf import PageObject


def _pages_from_size(document_size: int, booklet_size: int) -> Generator[range, None, None]:
    total_booklets, remaining = divmod(document_size, booklet_size)
    return cast(Generator[range, None, None], chain(
        (range(i*booklet_size, i*booklet_size+booklet_size) for i in range(total_booklets)),
        repeat(range(document_size-remaining, document_size), 1)
    ))


def split_pages_with_size(pdf: PdfFileReader, booklet_size: int) -> Generator[Generator[PageObject, None, None], None, None]:
    yield from map(
        lambda pages: map(pdf.getPage, pages),
        _pages_from_size(pdf.getNumPages(), booklet_size=booklet_size)
    )


def split_pdf_with_size(path: Path, reader: PdfFileReader, size: int) -> Generator[int, None, None]:
    for i, booklet in enumerate(split_pages_with_size(reader, size)):
        writer = PdfFileWriter()

        for page in booklet:
            writer.addPage(page)

        suffix: str = path.suffix
        file_name: str = path.name.rstrip(suffix)
        parent_dir: Path = path.parent
        file_path: Path = parent_dir / f"{file_name}_{i:>04}{suffix}"

        with open(file_path, 'wb') as outfile:
            writer.write(outfile)
        yield i


if __name__ == "__main__":
    import sys
    _, size, pdf, *_ = sys.argv
    pdf = Path(pdf)
    with open(pdf, 'rb') as f:
        reader = PdfFileReader(f)
        for i in split_pdf_with_size(pdf, reader, int(size)):
            print(f"Writing booklet {i}")
