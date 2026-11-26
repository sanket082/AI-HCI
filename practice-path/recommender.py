"""Rank original software practice exercises using a catalog-fitted TF-IDF model."""
import argparse
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CATALOG = Path(__file__).with_name("catalog.csv")


class PracticePath:
    def __init__(self):
        with CATALOG.open(encoding="utf-8", newline="") as source:
            self.items = list(csv.DictReader(source))
        self.by_id = {item["id"]: i for i, item in enumerate(self.items)}
        documents = [" ".join(item[k] for k in ("title", "tags", "task")) for item in self.items]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(documents).tocsr()
        self.words = self.vectorizer.get_feature_names_out()

    def recommend(self, goal="", liked=None, minutes=60):
        profile = self.vectorizer.transform([goal])
        seed_only = liked and profile.nnz == 0
        if liked:
            seed_tags = set(self.items[self.by_id[liked]]["tags"].split())
            profile = normalize(profile + self.matrix[[self.by_id[liked]]])
        if profile.nnz == 0:
            return [], "Try a catalog topic such as SQL or choose a liked exercise with --like."
        matches = []
        for i, item in enumerate(self.items):
            if item["id"] == liked or int(item["minutes"]) > minutes:
                continue
            if seed_only and seed_tags.isdisjoint(item["tags"].split()):
                continue
            contributions = self.matrix[[i]].multiply(profile).tocoo()
            score = float(contributions.sum())
            if score > 0:
                terms = sorted(zip(contributions.data, contributions.col),
                               key=lambda pair: (-pair[0], self.words[pair[1]]))
                matches.append((item, score, [self.words[col] for _, col in terms[:3]]))
        matches.sort(key=lambda match: (-match[1], match[0]["id"]))
        return matches[:3], "" if matches else "No matching exercise fits. Increase the time or change the goal."


def main():
    model = PracticePath()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="show exercise IDs, times and topics")
    parser.add_argument("--goal", help="keywords describing what you want to practice")
    parser.add_argument("--like", choices=sorted(model.by_id), help="an exercise you enjoyed")
    parser.add_argument("--minutes", type=int, default=60, help="maximum minutes per exercise")
    args = parser.parse_args()
    if args.minutes < 1:
        parser.error("--minutes must be positive")
    if args.list:
        for item in model.items:
            print(f"{item['id']:10} {item['minutes']} min | {item['title']} | {item['tags']}")
        return
    goal = args.goal
    if goal is None and not args.like:
        goal = input("What would you like to practice? (e.g., SQL joins) ")
    matches, message = model.recommend(goal or "", args.like, args.minutes)
    if message:
        print(message)
    for rank, (item, score, terms) in enumerate(matches, 1):
        print(f"{rank}. {item['title']} ({item['minutes']} min) [{item['id']}]")
        print(f"   {item['task']}")
        print(f"   Shared terms: {', '.join(terms)} | Similarity: {score:.3f}")


if __name__ == "__main__":
    main()
