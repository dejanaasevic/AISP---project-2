import re

def search_document(trie, graph, document_text, query):
    query = query.lower()
    pages = document_text.split('--- Page ')[1:]
    search_results = []
    pink_start = "\033[95m"
    pink_end = "\033[0m"
    query_words = query.split()

    for page_index, page_text in enumerate(pages):
        page_number = page_index + 1
        contexts = []
        total_score = 0
        found_query_words = []

        # Count occurrences of each query word
        word_counts = {word: 0 for word in query_words}

        # Find all occurrences of query words and count them
        for query_word in query_words:
            occurrences = page_text.lower().count(query_word)
            if occurrences > 0:
                found_query_words.append(query_word)
            word_counts[query_word] = occurrences

        # Calculate total score based on word counts
        for count in word_counts.values():
            total_score += count

        # Highlight all query words in the context
        if found_query_words:
            query_pattern = re.compile(r'.{0,250}(' + '|'.join(map(re.escape, query_words)) + r').{0,250}', re.IGNORECASE)
            for match in query_pattern.finditer(page_text):
                context = match.group()
                highlighted_context = context
                for query_word in query_words:
                    highlighted_context = re.sub(re.escape(query_word), f'{pink_start}{query_word}{pink_end}', highlighted_context, flags=re.IGNORECASE)
                contexts.append(highlighted_context)

            search_results.append((page_number, contexts, total_score, len(set(query_words) & set(found_query_words))))

    # Sort results: pages with all query words first, then by total_score descending
    search_results.sort(key=lambda x: (x[3], x[2], x[0]), reverse=True)

    return search_results
