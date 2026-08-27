"""
Web Search Agent
-----------------
Takes a startup idea (plus optional product name, industry, and target audience),
validates language coherence, extracts the core domain focus, and executes
searches structured across 4 distinct market categories:
  1. Competitors
  2. Industry News
  3. Customer Demand
  4. Market Size & Trends
"""

import urllib.request
import urllib.parse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from lxml import html as lxml_html, etree
import wordfreq

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

# Regex patterns matching conversational starter phrases to strip from free-text ideas
CONVERSATIONAL_PATTERNS = [
    r"\b(i want to (create|build|make|develop|launch|start))\b",
    r"\b(an? (app|platform|tool|service|system|website|software) (that|which|to|for))\b",
    r"\b(a (platform|tool|service|system|product) (for|that|to))\b",
    r"\b(looking to (build|create|make|launch|develop))\b",
    r"\b(we are (building|creating|making|launching|developing))\b",
    r"\b(helps? (people|users|teams|customers))\b",
    r"\b(based on (my|your|our|their))\b",
    r"\b(i am (trying|planning|hoping) to)\b",
]

# Stopwords, pronouns, and conversational filler words to filter out during keyword extraction
PROCEDURAL_STOPWORDS = {
    "and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "it", "its", "this", "that", "these", "those", "as", "be",
    "has", "have", "had", "do", "does", "did", "will", "would", "could", "should", "can",
    "into", "also", "when", "where", "which", "who", "how", "why", "what", "such", "one",
    "more", "most", "some", "any", "all", "each", "every", "both", "few", "than", "then",
    "i", "me", "my", "myself", "we", "our", "ours", "you", "your", "yours", "he", "him", "his",
    "she", "her", "they", "them", "their", "theirs",
    "want", "wants", "wanted", "wanting",
    "create", "creates", "created", "creating",
    "build", "builds", "built", "building",
    "make", "makes", "made", "making",
    "develop", "develops", "developed", "developing",
    "launch", "launches", "launched", "launching",
    "start", "starts", "started", "starting",
    "help", "helps", "helped", "helping",
    "need", "needs", "needed", "needing",
    "look", "looks", "looking",
    "try", "tries", "trying", "tried",
    "base", "based", "bases", "basing",
    "suggest", "suggests", "suggesting",
    "platform", "system", "tool", "service", "app", "apps", "application", "applications",
    "online", "digital", "simple", "startup", "product", "products", "idea", "ideas",
    "user", "users", "people", "something", "someone", "thing", "things",
    "enter", "manually", "automatically", "combining", "provides", "tracks", "breaks", "identifies",
    "manageable", "daily", "tasks", "completed", "weak", "future", "fall", "behind",
    "generate", "short", "notes", "key", "differentiation", "progress", "tracking",
}

# Additional procedural terms to avoid in long descriptions (general verbs and generic utility nouns)
PROCEDURAL_UTILITY_TERMS = {
    "appointment", "appointments", "schedule", "scheduling", "manage", "managing", "management",
    "information", "data", "feature", "features", "workflow", "process", "processes",
    "integration", "integrate", "update", "updates", "notification", "notifications",
    "reminder", "reminders", "alert", "alerts", "send", "sending", "receive", "receiving",
    "access", "accessing", "store", "storing", "save", "saving", "load", "loading",
    "display", "displaying", "show", "showing", "view", "viewing", "connect", "connecting",
    "sync", "syncing", "share", "sharing", "export", "exporting", "import", "importing",
}


def clean_query_text(text: str) -> str:
    """Removes special characters and collapses excess whitespace."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return ' '.join(cleaned.split())


class WebSearchAgent:
    """Agent responsible for idea validation, semantic concept extraction, and 4-category market research."""

    def is_valid_idea(self, text: str) -> bool:
        """
        Validates whether the idea text contains recognizable English words.
        Prevents gibberish or nonsense input from triggering search fallbacks.
        """
        if not text or len(text.strip()) < 5:
            return False

        words = re.findall(r'[a-zA-Z]+', text)
        if not words or len(words) < 2:
            return False

        valid_count = sum(1 for w in words if wordfreq.word_frequency(w.lower(), 'en') > 0)
        ratio = valid_count / len(words)

        return valid_count >= 2 and ratio >= 0.45

    def extract_core_keywords(
        self,
        idea: str,
        industry: str | None = None,
        name: str | None = None,
    ) -> str:
        """
        Extracts high-signal domain keywords by stripping conversational fillers,
        prioritizing explicit industry categories, and retaining the top domain nouns.
        For longer texts (>150 chars), filters out general verbs and utility terms,
        prioritizing domain-specific subject nouns.
        """
        # 1. If industry is provided and non-empty, prioritize it
        if industry and industry.strip():
            ind_clean = clean_query_text(industry)
            ind_tokens = [
                w.lower() for w in re.findall(r'[a-zA-Z0-9]+', ind_clean)
                if w.lower() not in PROCEDURAL_STOPWORDS and len(w) > 2
            ]
            if ind_tokens:
                name_clean = clean_query_text(name or '') if name else ''
                name_tokens = [
                    w.lower() for w in re.findall(r'[a-zA-Z0-9]+', name_clean)
                    if w.lower() not in PROCEDURAL_STOPWORDS and len(w) > 2
                ]

                # Also extract high-signal idea keywords to complement the industry
                cleaned_idea = idea
                for pat in CONVERSATIONAL_PATTERNS:
                    cleaned_idea = re.sub(pat, " ", cleaned_idea, flags=re.IGNORECASE)
                idea_words = [
                    w.lower() for w in re.findall(r'[a-zA-Z0-9]+', cleaned_idea)
                    if w.lower() not in PROCEDURAL_STOPWORDS and len(w) > 2
                ]

                combined_tokens = []
                for tok in ind_tokens + name_tokens + idea_words[:3]:
                    if tok not in combined_tokens:
                        combined_tokens.append(tok)
                return " ".join(combined_tokens[:4])

        # 2. If industry is empty, strip conversational patterns from idea
        cleaned_idea = idea
        for pat in CONVERSATIONAL_PATTERNS:
            cleaned_idea = re.sub(pat, " ", cleaned_idea, flags=re.IGNORECASE)

        # Extract remaining words
        raw_words = re.findall(r'[a-zA-Z0-9]+', cleaned_idea)
        
        # Determine if this is a long description requiring enhanced filtering
        is_long_description = len(idea.strip()) > 150
        
        # Apply enhanced filtering for longer descriptions
        if is_long_description:
            # Filter out both procedural stopwords and utility terms for long descriptions
            candidate_words = [
                w.lower() for w in raw_words
                if (w.lower() not in PROCEDURAL_STOPWORDS and 
                    w.lower() not in PROCEDURAL_UTILITY_TERMS and 
                    len(w) > 2)
            ]
        else:
            # Standard filtering for shorter descriptions
            candidate_words = [
                w.lower() for w in raw_words
                if w.lower() not in PROCEDURAL_STOPWORDS and len(w) > 2
            ]

        # Find domain-specific terms by looking for repeated or domain-anchored words
        word_frequency = {}
        for word in candidate_words:
            word_frequency[word] = word_frequency.get(word, 0) + 1

        # Score words by specificity and domain relevance
        scored_words = []
        for w in candidate_words:
            freq = wordfreq.word_frequency(w, 'en')
            # Lower frequency -> higher specificity score
            specificity_score = 1.0 - freq if freq > 0 else 0.99
            
            # Boost score for words that appear multiple times (domain anchors)
            repetition_boost = min(word_frequency[w] * 0.1, 0.3)
            
            # Boost score for words that are likely domain-specific nouns
            # Check if word ends with common noun suffixes or is a concrete noun
            domain_boost = 0.0
            if (w.endswith(('tion', 'ness', 'ment', 'ing', 'er', 'or', 'ist', 'ian')) or
                w in {'health', 'care', 'medical', 'clinic', 'hospital', 'doctor', 'patient',
                      'pet', 'dog', 'cat', 'animal', 'vet', 'veterinary', 'grooming',
                      'food', 'restaurant', 'kitchen', 'recipe', 'cooking', 'meal',
                      'education', 'student', 'teacher', 'school', 'learning', 'course',
                      'fitness', 'exercise', 'workout', 'gym', 'training', 'sport',
                      'finance', 'money', 'payment', 'banking', 'investment', 'budget',
                      'travel', 'hotel', 'booking', 'flight', 'vacation', 'trip',
                      'business', 'company', 'client', 'customer', 'sales', 'marketing',
                      'property', 'house', 'real', 'estate', 'rent', 'lease',
                      'music', 'audio', 'video', 'media', 'content', 'creative'}):
                domain_boost = 0.2
                
            final_score = specificity_score + repetition_boost + domain_boost
            scored_words.append((final_score, w))

        # Preserve order of highest signal terms, avoiding duplicates
        seen = set()
        top_keywords = []

        # Include product name first if provided
        if name and name.strip():
            name_clean = clean_query_text(name)
            for nw in re.findall(r'[a-zA-Z0-9]+', name_clean):
                if (nw.lower() not in PROCEDURAL_STOPWORDS and 
                    nw.lower() not in PROCEDURAL_UTILITY_TERMS and 
                    nw.lower() not in seen and len(nw) > 2):
                    seen.add(nw.lower())
                    top_keywords.append(nw.lower())

        # Add highest scoring domain words
        for _, w in sorted(scored_words, key=lambda x: x[0], reverse=True):
            if w not in seen:
                seen.add(w)
                top_keywords.append(w)
                if len(top_keywords) >= 4:
                    break

        # Ensure we have at least one domain anchor noun
        if not top_keywords or (is_long_description and not any(
            kw for kw in top_keywords if kw not in PROCEDURAL_UTILITY_TERMS
        )):
            # Fallback: find the most domain-specific words from the original candidates
            domain_candidates = [w for w in candidate_words if w not in PROCEDURAL_UTILITY_TERMS]
            if domain_candidates:
                top_keywords = domain_candidates[:3]
            else:
                # Last resort fallback
                top_keywords = candidate_words[:3] or raw_words[:3]

        return " ".join(top_keywords)

    def extract_domain_focus(
        self,
        idea: str,
        industry: str | None = None,
        product_name: str | None = None,
    ) -> str:
        """Backwards-compatible wrapper around extract_core_keywords."""
        return self.extract_core_keywords(idea, industry=industry, name=product_name)

    def get_meaningful_keywords(
        self,
        idea: str,
        industry: str | None = None,
        product_name: str | None = None,
    ) -> set[str]:
        """Extracts meaningful non-stopword domain terms for relevance filtering."""
        core_kw_str = self.extract_core_keywords(idea, industry, product_name)
        tokens = set(re.findall(r'[a-zA-Z]{3,}', core_kw_str.lower()))

        # Also extract non-stopword tokens from the stripped idea text
        clean_idea = idea
        for pat in CONVERSATIONAL_PATTERNS:
            clean_idea = re.sub(pat, " ", clean_idea, flags=re.IGNORECASE)
        idea_tokens = {
            w.lower() for w in re.findall(r'[a-zA-Z]{3,}', clean_idea)
            if w.lower() not in PROCEDURAL_STOPWORDS
        }
        return tokens.union(idea_tokens)

    def build_queries(
        self,
        extracted_keywords: str,
        industry: str | None = None,
        target_audience: str | None = None,
    ) -> list[tuple[str, list[str]]]:
        """Generates clean, category-specific search queries using extracted keywords."""
        kw = extracted_keywords.strip()
        aud = clean_query_text(target_audience or '') if target_audience and target_audience.strip() else ""

        return [
            ("Competitors", [
                f'{kw} competitors alternatives startup',
                f'{kw} competitors alternatives apps',
            ]),
            ("Industry News", [
                f'{kw} startup news venture funding',
                f'{kw} industry market news 2026',
            ]),
            ("Customer Demand", [
                f'{kw} customer demand pain points',
                f'{kw} {aud} user reviews feedback' if aud else f'{kw} customer demand adoption problems',
            ]),
            ("Market Size & Trends", [
                f'{kw} market size industry growth trends',
                f'{kw} market size growth report forecast',
            ]),
        ]

    def _search_ddg_html(self, query: str, max_results: int = 5) -> list[dict]:
        """Queries DuckDuckGo HTML endpoint directly with clean headers."""
        url = "https://html.duckduckgo.com/html/"
        clean_q = clean_query_text(query)
        data = urllib.parse.urlencode({"q": clean_q}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        results = []
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                tree = lxml_html.fromstring(content)
                for i, body in enumerate(tree.xpath("//div[contains(@class, 'result__body')]")[:max_results]):
                    title_links = body.xpath(".//a[contains(@class, 'result__a')]")
                    snippets = body.xpath(".//a[contains(@class, 'result__snippet')]")
                    if title_links:
                        title = title_links[0].text_content().strip()
                        raw_url = title_links[0].get("href", "")
                        if "uddg=" in raw_url:
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                            clean_url = parsed.get("uddg", [raw_url])[0]
                        else:
                            clean_url = raw_url
                        snippet = snippets[0].text_content().strip() if snippets else ""
                        if clean_url and title:
                            results.append({
                                "title": title,
                                "url": clean_url,
                                "content": snippet,
                                "score": round(1.0 - (i * 0.08), 2),
                            })
        except Exception:
            pass

        # Try ddgs library if HTML scraper was sparse
        if not results and DDGS is not None:
            try:
                with DDGS(timeout=3) as ddgs:
                    hits = list(ddgs.text(clean_q, max_results=max_results))
                    for i, hit in enumerate(hits):
                        results.append({
                            "title": hit.get("title", ""),
                            "url": hit.get("href", ""),
                            "content": hit.get("body", ""),
                            "score": round(1.0 - (i * 0.08), 2),
                        })
            except Exception:
                pass

        return results

    def _search_google_news(self, query: str, max_results: int = 5) -> list[dict]:
        """Fetches live market news coverage via RSS for fresh signals."""
        clean_q = clean_query_text(query)
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(clean_q)}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        results = []
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                xml_data = resp.read()
                root = etree.fromstring(xml_data)
                for i, item in enumerate(root.xpath("//item")[:max_results]):
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    desc = item.findtext("description", "")
                    if desc:
                        try:
                            desc = lxml_html.fromstring(desc).text_content()
                        except Exception:
                            pass
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "content": desc or title,
                            "score": round(0.95 - (i * 0.07), 2),
                        })
        except Exception:
            pass
        return results

    def _filter_by_keyword_relevance(self, items: list[dict], keywords: set[str]) -> list[dict]:
        """Ensures fallback results contain at least one meaningful domain term."""
        if not keywords:
            return items

        filtered = []
        for item in items:
            text = f"{item.get('title', '')} {item.get('content', '')}".lower()
            if any(kw in text for kw in keywords):
                filtered.append(item)
        return filtered

    def _execute_category_search(
        self,
        category: str,
        queries: list[str],
        meaningful_keywords: set[str],
        max_results: int = 4,
    ) -> dict:
        """Executes multi-source search tailored to each specific category."""
        results = []

        # 1. Primary news search
        for q in queries:
            if len(results) >= max_results:
                break
            news = self._search_google_news(q, max_results=max_results)
            results.extend(self._filter_by_keyword_relevance(news, meaningful_keywords))

        # 2. DDG search
        if len(results) < max_results:
            for q in queries:
                if len(results) >= max_results:
                    break
                ddg = self._search_ddg_html(q, max_results=max_results - len(results))
                results.extend(self._filter_by_keyword_relevance(ddg, meaningful_keywords))

        return {
            "category": category,
            "query": queries[0] if queries else "",
            "response": {"results": results[:max_results]},
        }

    def search(
        self,
        idea: str,
        product_name: str | None = None,
        industry: str | None = None,
        target_audience: str | None = None,
        max_results_per_category: int = 4,
    ) -> list[dict]:
        """
        Executes parallel searches for the 4 distinct market categories:
          - Competitors
          - Industry News
          - Customer Demand
          - Market Size & Trends
        """
        core_keywords = self.extract_core_keywords(idea, industry, product_name)
        meaningful_keywords = self.get_meaningful_keywords(idea, industry, product_name)
        category_queries = self.build_queries(core_keywords, industry, target_audience)

        raw_batches = []
        with ThreadPoolExecutor(max_workers=len(category_queries)) as executor:
            futures = [
                executor.submit(
                    self._execute_category_search,
                    cat,
                    queries,
                    meaningful_keywords,
                    max_results_per_category,
                )
                for cat, queries in category_queries
            ]
            for future in futures:
                try:
                    raw_batches.append(future.result())
                except Exception:
                    pass

        return raw_batches
