import math

def normalize(text: str) -> str:
    """Normalize text: lowercase and keep only letters, numbers, and whitespace."""
    return "".join(c for c in text.lower() if c.isalnum() or c.isspace())

class FuzzyMatcher:
    def __init__(self):
        self.source_text = ""
        self.normalized_source = ""
        self.match_start_offset = 0
        self.recognized_char_count = 0

    def set_text(self, text: str):
        """Initialize with new script text."""
        # Simple cleanup of lines
        self.source_text = " ".join(text.split())
        self.normalized_source = normalize(self.source_text)
        self.match_start_offset = 0
        self.recognized_char_count = 0

    def jump_to(self, char_offset: int):
        """Manual jump to position."""
        self.recognized_char_count = max(0, min(char_offset, len(self.source_text)))
        self.match_start_offset = self.recognized_char_count

    def get_prev_word_offset(self) -> int:
        """Find the start of the previous word."""
        pos = self.recognized_char_count - 2 # Skip current space if at boundary
        if pos < 0: return 0
        
        # Move back to find start of current/prev word
        while pos > 0 and self.source_text[pos].isspace():
            pos -= 1
        while pos > 0 and not self.source_text[pos-1].isspace():
            pos -= 1
        return pos

    def get_next_word_offset(self) -> int:
        """Find the start of the next word."""
        pos = self.recognized_char_count
        if pos >= len(self.source_text): return len(self.source_text)
        
        # Skip current word
        while pos < len(self.source_text) and not self.source_text[pos].isspace():
            pos += 1
        # Skip spaces
        while pos < len(self.source_text) and self.source_text[pos].isspace():
            pos += 1
        return pos

    def match(self, spoken_text: str) -> int:
        """
        Process new spoken text and return the current character position in source.
        Matches from the current `match_start_offset`.
        """
        if not spoken_text.strip():
            return self.recognized_char_count

        # Strategy 1: Char-level match
        char_result = self._char_level_match(spoken_text)
        
        # Strategy 2: Word-level match (better for skipped words/substitutions)
        word_result = self._word_level_match(spoken_text)

        best_match = max(char_result, word_result)
        
        new_count = self.match_start_offset + best_match
        
        # NEVER MOVE BACKWARDS
        if new_count > self.recognized_char_count:
            self.recognized_char_count = min(new_count, len(self.source_text))
            
        return self.recognized_char_count

    def _char_level_match(self, spoken: str) -> int:
        remaining_source = self.source_text[self.match_start_offset:]
        src = [c for c in normalize(remaining_source)]
        spk = [c for c in normalize(spoken)]

        si = 0  # source index
        ri = 0  # spoken index
        last_good_orig_index = 0
        
        src_orig_idx = 0
        
        while si < len(src) and ri < len(spk):
            while src_orig_idx < len(remaining_source):
                if normalize(remaining_source[src_orig_idx]) == src[si]:
                    break
                src_orig_idx += 1

            if src_orig_idx >= len(remaining_source):
                break

            if src[si] == spk[ri]:
                si += 1
                ri += 1
                last_good_orig_index = src_orig_idx + 1
                src_orig_idx += 1
            else:
                found = False
                # Skip in Spoken (extra)
                max_skip_r = min(3, len(spk) - ri - 1)
                for skip_r in range(1, max_skip_r + 1):
                    if spk[ri + skip_r] == src[si]:
                        ri += skip_r
                        found = True
                        break
                if found: continue

                # Skip in Source (missed)
                max_skip_s = min(3, len(src) - si - 1)
                for skip_s in range(1, max_skip_s + 1):
                    if src[si + skip_s] == spk[ri]:
                        si += skip_s
                        found = True
                        break
                if found: continue
                
                # Substitution
                si += 1
                ri += 1
                last_good_orig_index = src_orig_idx + 1
                src_orig_idx += 1
        
        return last_good_orig_index

    def _word_level_match(self, spoken: str) -> int:
        remaining_source = self.source_text[self.match_start_offset:]
        source_words = remaining_source.split(" ")
        spoken_words = spoken.lower().split()
        
        si = 0
        ri = 0
        matched_char_count = 0
        
        while si < len(source_words) and ri < len(spoken_words):
            if self._is_annotation(source_words[si]):
                matched_char_count += len(source_words[si]) + 1
                si += 1
                continue
                
            src_word = "".join(filter(str.isalnum, source_words[si].lower()))
            spk_word = "".join(filter(str.isalnum, spoken_words[ri]))
            
            if src_word == spk_word or self._is_fuzzy_match(src_word, spk_word):
                matched_char_count += len(source_words[si]) + 1
                si += 1
                ri += 1
            else:
                # Look ahead spoken (hallucination)
                found_spk = False
                max_spk_skip = min(3, len(spoken_words) - ri - 1)
                for skip in range(1, max_spk_skip + 1):
                    next_spk = "".join(filter(str.isalnum, spoken_words[ri + skip]))
                    if src_word == next_spk or self._is_fuzzy_match(src_word, next_spk):
                        ri += skip
                        found_spk = True
                        break
                if found_spk: continue
                
                # Look ahead source (missed words)
                found_src = False
                max_src_skip = min(5, len(source_words) - si - 1)
                for skip in range(1, max_src_skip + 1):
                    next_src = "".join(filter(str.isalnum, source_words[si + skip].lower()))
                    if next_src == spk_word or self._is_fuzzy_match(next_src, spk_word):
                        for k in range(skip):
                            matched_char_count += len(source_words[si+k]) + 1
                        si += skip
                        found_src = True
                        break
                if found_src: continue
                
                if not src_word:
                    matched_char_count += len(source_words[si]) + 1
                    si += 1
                    continue
                    
                ri += 1
                
        while si < len(source_words) and self._is_annotation(source_words[si]):
            matched_char_count += len(source_words[si]) + 1
            si += 1
            
        return matched_char_count

    def _is_annotation(self, word: str) -> bool:
        if word.startswith("[") and word.endswith("]"): return True
        return not any(c.isalnum() for c in word)

    def _is_fuzzy_match(self, a: str, b: str) -> bool:
        if not a or not b: return False
        if a == b: return True
        
        shorter = min(len(a), len(b))
        shared = 0
        for c1, c2 in zip(a, b):
            if c1 == c2: shared += 1
            else: break
        
        if shorter >= 3 and shared >= max(3, int(shorter * 0.5)): return True
        if a in b or b in a: return True
        
        dist = self._edit_distance(a, b)
        if shorter <= 4: return dist <= 1
        if shorter <= 8: return dist <= 2
        return dist <= max(len(a), len(b)) // 3

    def _edit_distance(self, a: str, b: str) -> int:
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1): dp[i][0] = i
        for j in range(n + 1): dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1]
                else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        return dp[m][n]
