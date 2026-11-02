# Azure Sentiment Chatbot

Traditional Python CLI chatbot integrated with Azure AI Language sentiment analysis using the **Free F0 tier**.

Project URL: https://github.com/sanket082/AI-HCI/tree/main/azure-sentiment-chatbot

## Status and provenance

Original rule-based bot created for the attached University of the Cumberlands assignment; no earlier bot source was copied. Azure integration follows Microsoft's Python SDK documentation. ChatGPT assisted with implementation, tests, documentation, and report drafting. Review and personalize the report before submission.

**Local verification completed; live Azure verification pending.** Tests mock the SDK boundary and do not call Azure. No Azure resource was provisioned during preparation. The application itself always uses real Azure for analysis and has no fake sentiment fallback.

## Run

Requires Python 3.11+. From this directory:

```bash
python -m venv .venv
# Bash:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py
```

Try `hello`, `help`, `capabilities`, `examples`, `about`, and `quit`. Use `sentiment: I love this service.` or any plain English sentence for cloud analysis. Blank input, control characters, unknown slash commands, and text over 1000 characters receive actionable local feedback. Multiple prompts work in one session.

## Azure free-tier setup

1. Sign in at https://portal.azure.com with your Azure subscription; an eligible student subscription is suitable.
2. Create a **Language** resource (portal branding may refer to Language in Foundry Tools) in a dedicated resource group and supported region. Omit optional custom question answering/Search resources.
3. Explicitly select **Free F0** and review the responsible AI notice. If F0 is unavailable, stop and resolve subscription, region, or existing-resource constraints instead of choosing a paid SKU.
4. Review and create. Open **Keys and Endpoint**. Copy the matching endpoint and key into local environment variables. Never paste secrets into chat, screenshots, GitHub, or the ZIP.
5. Set variables in the same terminal that runs Python:

```powershell
# Windows PowerShell
$env:AZURE_LANGUAGE_ENDPOINT = Read-Host 'Language endpoint'
$secret = Read-Host 'Language key' -AsSecureString
$env:AZURE_LANGUAGE_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
python app.py
```

```bash
# Bash
read -r -p 'Language endpoint: ' AZURE_LANGUAGE_ENDPOINT
export AZURE_LANGUAGE_ENDPOINT
read -r -s -p 'Language key: ' AZURE_LANGUAGE_KEY
export AZURE_LANGUAGE_KEY
printf '\n'
python app.py
```

`.env.example` is documentation only: the app does not automatically load .env files. Without credentials, local commands work and analysis returns an actionable configuration message.

Microsoft currently lists 5,000 shared free text records per month across applicable Language features, measured in 1,000-character units. Check the offer in your portal. The application's input cap reduces request size; it does not enforce an account-wide quota. F0 differs from temporary Azure account credits. Automatic SDK retries are disabled, and the bot handles HTTP 429 with a manual retry/usage message.

## Live acceptance and screenshots still required

After configuring F0, send these in one session and record actual labels and scores (do not force expected outcomes):

- `help`
- `sentiment: I love this service.`
- `sentiment: My delivery was late and damaged.`
- `sentiment: The shop opens at nine.`
- `sentiment: The staff were helpful, but the product broke.`
- A blank line, `sentiment:`, and `/unknown`
- `quit`

Capture the resource overview with F0 visible and a terminal showing genuine Azure responses. Hide subscription identifiers and secrets; do not show keys. Add these verified screenshots to the report. Existing evidence only documents local execution and mocked tests. A synthetic-output screenshot must never be presented as a cloud result.

## Architecture and limitations

`app.py` manages the CLI loop. `bot.py` separates deterministic routing from `AzureAnalyzer`, a lazy `TextAnalyticsClient` adapter. Analysis explicitly uses English. Connection/read timeouts are 5/15 seconds, with retries disabled. SDK exceptions are sanitized; request text, credentials, and raw exceptions are not logged. There is no persistent conversation history. Submitted synthetic test transcripts are intentionally recorded for this assignment.

Confidence scores describe model output, not measured accuracy or a diagnosis of a person's emotions. This bot does not generate answers to general questions. Sarcasm, context, domain language, accessibility, and multilingual support need further evaluation. Production improvements include managed identity, representative evaluation data, privacy-preserving monitoring, and rate limiting across users.

## Evidence and files

- `app.py`, `bot.py`: application source.
- `tests/test_bot.py`: 11 tests including subcases, using mocks.
- `requirements.txt`: direct SDK version; `evidence/environment.txt` records resolved versions.
- `.env.example`, `.gitignore`: configuration guidance and exclusions.
- `evidence/test-results.txt`: actual test run.
- `evidence/local-session.txt`: actual no-credentials CLI run.

Coverage includes local routing, invalid input, repeated prompts, input boundary, recovery, Azure response mapping, missing credentials, invalid endpoint, document errors, HTTP 401/403/429/500, and network failures. Model accuracy and live subscription behavior are not established by these tests.

## References

- Microsoft. Python SDK: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-textanalytics-readme?view=azure-python
- Microsoft. Quickstart: https://learn.microsoft.com/azure/ai-services/language-service/sentiment-opinion-mining/quickstart?pivots=programming-language-python
- Microsoft. Pricing: https://azure.microsoft.com/en-us/pricing/details/language/
