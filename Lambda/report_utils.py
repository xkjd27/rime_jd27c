"""Shared parsing helpers for the generated 报告 (report) files."""


def iter_dup_report(path):
    """Yield ``(code, dups)`` records from a 词组重码报告 duplicate-code report.

    The report lists, after a ``---`` separator, blocks of the form::

        <code>
        <rank>\t<word>
        <rank>\t<word>
        <blank line>

    ``code`` is the duplicated code string and ``dups`` is a list of
    ``[rank, word]`` pairs (each split on tab). Iteration stops at the next
    ``---`` separator or end of the block section.
    """
    with open(path, mode='r', encoding='utf-8') as infile:
        # Skip the summary header up to the first separator.
        for line in infile:
            if line.strip() == '---':
                break

        while True:
            line = infile.readline()
            if len(line.strip()) == 0 or line.strip() == '---':
                break

            code = line.strip()
            dups = []
            data = infile.readline().strip()
            while len(data) > 0:
                dups.append(data.split('\t'))
                data = infile.readline().strip()

            yield code, dups
