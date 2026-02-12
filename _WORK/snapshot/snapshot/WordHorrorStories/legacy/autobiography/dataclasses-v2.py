@dataclass
class LogEntry:
    version: str
    id: str
    session_id: str
    ts_iso: str
    ts_jalali: str
    source: str
    model: str | None
    project_path: str | None
    workspace: str | None
    q_text: str
    a_text: str
    q_summary: str | None
    a_summary: str | None
    language_guess: str | None
    tags: list[str] | None

class LogFileReader:
    def __init__(self, paths: list[str])
    def __iter__(self) -> Iterator[LogEntry]
    def validate(self, entry_dict) -> LogEntry

class LogCollection:
    def __init__(self, entries: Iterable[LogEntry])
    def sort_by_iso(self)
    def group_by(self, field: str) -> OrderedDict[str, list[LogEntry]]
    def unique(self) -> "LogCollection"  # remove duplicates by id

@dataclass
class DocxConfig:
    title: str = "Coding Autobiography"
    group_field: str = "ts_jalali_date"
    heading_styles: dict[str, str] = field(default_factory=lambda: {"h1": "Heading 1", "h2": "Heading 2"})

class DocxBuilder:
    def __init__(self, config: DocxConfig)
    def append_entries(self, grouped: OrderedDict[str, list[LogEntry]], output_path: str)

def main():
    parse CLI args into ChronicleConfig
    reader = LogFileReader(input_paths)
    collection = LogCollection(reader)
    collection = collection.unique().sort_by_iso()
    grouped = collection.group_by(config.group_field)
    builder = DocxBuilder(docx_config)
    builder.append_entries(grouped, output_docx)
