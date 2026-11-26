# Practice Path
A local text-based recommender for twelve original software practice exercises. It ranks exercises using a goal, a previously enjoyed exercise, or both. Each result contains a task, estimated duration, and the words contributing most to its similarity score.

## Run
Tested with Python 3.12 and scikit-learn 1.8.0. In the extracted practice-path folder, optionally activate a virtual environment, then run:

    python -m pip install -r requirements.txt
    python recommender.py
    python recommender.py --list
    python recommender.py --goal "SQL joins" --minutes 20
    python recommender.py --like mock
    python recommender.py --goal keyboard --like labels --minutes 20
    python -m unittest -v

The first application command prompts for a goal. Use --list to discover exercise IDs for --like. Internet access is needed to install missing dependencies. The application runs locally after installation and stores no user profile.

## Model and limitations
Fit one TF-IDF vocabulary on exercise titles, tags and tasks. Transform the goal with the same vocabulary and optionally add a liked item's unit vector, then normalize. Exclude the seed and over-budget exercises. If only the seed supplies recognized terms, require a shared topic tag. Return at most three positive cosine matches with deterministic ID tie-breaking. Reasons come from the largest products of shared term weights. Similarity is not a probability of success. Unknown vocabulary and multiple meanings can reduce relevance.

To extend the catalog, add a row to catalog.csv with a unique ID, title, positive whole-minute estimate, space-separated lowercase topic tags, and an actionable task. The model refits on startup. test_recommender.py covers ranking and edge cases.

## Credits
The starting example was the four-document Examples section of the scikit-learn TfidfVectorizer documentation: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html . This project uses the library and adapts the example's corpus-to-vector method. The catalog, recommendation logic, command-line interface, and tests were developed for this assignment with OpenAI ChatGPT assistance. No external learner records or ratings were used.

Project URL: https://github.com/sanket082/AI-HCI/tree/main/practice-path
