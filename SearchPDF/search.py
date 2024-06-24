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
        all_present = all(word in page_text.lower() for word in query_words)

        if all_present:
            total_score = 0
            for query_word in query_words:
                query_pattern = re.compile(r'.{0,250}' + re.escape(query_word) + r'.{0,250}', re.IGNORECASE)
                score = 0
                for match in query_pattern.finditer(page_text):
                    context = match.group()
                    score += 1
                    highlighted_context = re.sub(re.escape(query_word), f'{pink_start}{query_word}{pink_end}', context, flags=re.IGNORECASE)
                    contexts.append(highlighted_context)
                total_score += score
            search_results.append((page_number, contexts, total_score))
    search_results.sort(key=lambda x: x[2], reverse=True)
    return search_results
