import re


def parse_query(query):
    tokens = re.findall(r'\w+|AND|OR|NOT', query)
    return tokens


def evaluate_condition(page_text, tokens):
    page_text_lower = page_text.lower()
    found_words = set()
    total_score = 0
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == 'AND':
            index += 1
            continue
        elif token == 'OR':
            index += 1
            continue
        elif token == 'NOT':
            index += 1
            term = tokens[index].lower()
            index += 1
            if term in page_text_lower:
                return False, found_words, total_score
            continue
        else:
            term = token.lower()
            index += 1
            if term in page_text_lower:
                found_words.add(term)
                total_score += page_text_lower.count(term)
    return True, found_words, total_score


def search_document_by_conditions(trie, graph, document_text, query):
    tokens = parse_query(query)
    pages = document_text.split('--- Page ')[1:]
    search_results = []
    pink_start = "\033[95m"
    pink_end = "\033[0m"
    query_words = re.findall(r'\w+', query.lower())
    for page_index, page_text in enumerate(pages):
        page_number = page_index + 1
        contexts = []
        total_score = 0
        match, found_query_words, total_score = evaluate_condition(page_text, tokens)
        if match:
            query_pattern = re.compile(r'.{0,250}(' + '|'.join(map(re.escape, query_words)) + r').{0,250}',
                                       re.IGNORECASE)
            for match in query_pattern.finditer(page_text):
                context = match.group()
                highlighted_context = context
                highlighted = False
                for query_word in query_words:
                    if query_word.lower() not in {'and', 'or', 'not'}:
                        if re.search(re.escape(query_word), highlighted_context, flags=re.IGNORECASE):
                            highlighted_context = re.sub(re.escape(query_word), f'{pink_start}{query_word}{pink_end}',
                                                         highlighted_context, flags=re.IGNORECASE)
                            highlighted = True
                if highlighted:
                    contexts.append(highlighted_context)
            if contexts:
                total_score += sum(len(graph.get_reference(page_number)) for page_number in range(len(pages)))
                search_results.append((page_number, contexts, total_score, len(found_query_words)))
    search_results.sort(key=lambda x: (x[3], x[2], x[0]), reverse=True)
    return search_results


def search_document_by_phrase(trie, graph, document_text, query):
    query = query.lower()
    pages = document_text.split('--- Page ')[1:]
    search_results = []
    pink_start = "\033[95m"
    pink_end = "\033[0m"
    query_words = re.findall(r'"([^"]*)"', query)
    for page_index, page_text in enumerate(pages):
        page_number = page_index + 1
        contexts = []
        total_score = 0
        found_query_words = []
        for query_word in query_words:
            occurrences = page_text.lower().count(query_word)
            if occurrences > 0:
                found_query_words.append(query_word)
            total_score += occurrences
        if found_query_words:
            highlighted = False
            query_pattern = re.compile(r'.{0,250}(' + '|'.join(map(re.escape, query_words)) + r').{0,250}',
                                       re.IGNORECASE)
            for match in query_pattern.finditer(page_text):
                context = match.group()
                highlighted_context = context
                for query_word in query_words:
                    if query_word.lower() not in {'and', 'or', 'not'}:
                        highlighted_context = re.sub(re.escape(query_word), f'{pink_start}{query_word}{pink_end}',
                                                     highlighted_context, flags=re.IGNORECASE)
                        highlighted = True
                contexts.append(highlighted_context)
            if highlighted:
                total_score += sum(len(graph.get_reference(page_number)) for page_number in range(len(pages)))
                search_results.append(
                    (page_number, contexts, total_score, len(set(query_words) & set(found_query_words))))
    search_results.sort(key=lambda x: (x[3], x[2], x[0]), reverse=True)
    return search_results


def search_document(trie, graph, document_text, query):
    if any(keyword in query for keyword in ("NOT", "OR", "AND")):
        return search_document_by_conditions(trie, graph, document_text, query)
    if "\"" in query:
        return search_document_by_phrase(trie, graph, document_text, query)
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
        for query_word in query_words:
            occurrences = page_text.lower().count(query_word)
            if occurrences > 0:
                found_query_words.append(query_word)
            total_score += occurrences
        if found_query_words:
            highlighted = False
            query_pattern = re.compile(r'.{0,250}(' + '|'.join(map(re.escape, query_words)) + r').{0,250}',
                                       re.IGNORECASE)
            for match in query_pattern.finditer(page_text):
                context = match.group()
                highlighted_context = context
                for query_word in query_words:
                    if query_word.lower() not in {'and', 'or', 'not'}:
                        highlighted_context = re.sub(re.escape(query_word), f'{pink_start}{query_word}{pink_end}',
                                                     highlighted_context, flags=re.IGNORECASE)
                        highlighted = True
                contexts.append(highlighted_context)
            if highlighted:
                total_score += sum(len(graph.get_reference(page_number)) for page_number in range(len(pages)))
                search_results.append(
                    (page_number, contexts, total_score, len(set(query_words) & set(found_query_words))))
    search_results.sort(key=lambda x: (x[3], x[2], x[0]), reverse=True)
    return search_results
