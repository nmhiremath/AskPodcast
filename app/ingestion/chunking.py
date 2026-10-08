"""Chunking logic: Merges sequential Segments into retrieval-ready Chunks.

Uses a word-count sliding window while preserving exact timestamp bounds.
"""

from app.schemas import Chunk, Segment


def chunk_segments(
    segments: list[Segment],
    target_words: int = 200,
    overlap_words: int = 40,
) -> list[Chunk]:
    """Merge contiguous segments into chunks of ~target_words with overlap.

    If the speaker changes, we can also force a boundary to keep speaker attribution crisp.
    """
    if not segments:
        return []

    chunks: list[Chunk] = []
    chunk_index = 0
    i = 0
    n = len(segments)

    while i < n:
        current_segments: list[Segment] = []
        word_count = 0
        speaker = segments[i].speaker
        show = segments[i].show
        episode_id = segments[i].episode_id
        episode_title = segments[i].episode_title

        j = i
        while j < n:
            seg = segments[j]
            # Force boundary if speaker changes
            if seg.speaker != speaker:
                break

            seg_words = len(seg.text.split())
            current_segments.append(seg)
            word_count += seg_words
            j += 1

            if word_count >= target_words:
                break

        if not current_segments:
            i += 1
            continue

        chunk_text = " ".join(s.text for s in current_segments)
        chunks.append(
            Chunk(
                chunk_id=f"{episode_id}_c{chunk_index:04d}",
                show=show,
                episode_id=episode_id,
                episode_title=episode_title,
                speaker=speaker,
                start_seconds=current_segments[0].start_seconds,
                end_seconds=current_segments[-1].end_seconds,
                text=chunk_text,
            )
        )
        chunk_index += 1

        # Advance window with overlap
        if j >= n:
            break

        # Calculate how many segments to backtrack for overlap_words
        overlap_accum = 0
        step_back = 0
        for back_seg in reversed(current_segments):
            overlap_accum += len(back_seg.text.split())
            step_back += 1
            if overlap_accum >= overlap_words:
                break

        # Move i forward, guaranteeing progress (at least i + 1)
        next_i = j - step_back
        i = max(i + 1, next_i)

    return chunks
