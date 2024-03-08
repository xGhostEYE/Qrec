words = ["hello.world.hi", "hello", "world"]
for word in words:
    if '.' in word:
        parts = word.split('.')
        words.remove(word)
        for seperatedword in parts:
            words.append(seperatedword)
print(words)