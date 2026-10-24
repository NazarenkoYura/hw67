"""Подготовка данных оценки (часть B): golden, behavioral и индекс train-вопросов.

Golden: 52 авторских MCQ по статистике/ML (тема проекта — Cross Validated),
5 срезов: probability (12, критический), regression (10), hypothesis-testing (10),
machine-learning (10), distributions (10). Вопросы написаны вручную для ДЗ 6+7,
не копируют train-вопросы; правильные ответы проверены автором по стандартным
учебникам (Casella & Berger; ISLR; Wasserman "All of Statistics").

Позиция правильного варианта расставляется детерминированной ротацией A-D,
чтобы метки не слипались в одну букву.

Запуск: uv run python scripts/prepare_eval.py [--train-jsonl ПУТЬ]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# (срез, вопрос, правильный вариант, [неверные варианты x3])
QUESTIONS = [
    # --- probability (12) ---
    ("probability", "Two fair coins are tossed. What is the probability that both show heads?",
     "1/4", ["1/2", "1/3", "3/4"]),
    ("probability", "Events A and B are mutually exclusive with P(A) = 0.3 and P(B) = 0.4. What is P(A or B)?",
     "0.7", ["0.58", "0.12", "0.5"]),
    ("probability", "P(A) = 0.5 and P(B) = 0.4, and A and B are independent. What is P(A and B)?",
     "0.2", ["0.9", "0.1", "0.45"]),
    ("probability", "If P(A) = 0.3, what is the probability of the complement of A?",
     "0.7", ["0.3", "0.5", "0.09"]),
    ("probability", "What is the expected value of a single roll of a fair six-sided die?",
     "3.5", ["3", "4", "3.6"]),
    ("probability", "What is the variance of a Bernoulli random variable with success probability p?",
     "p(1-p)", ["p", "p squared", "1-p"]),
    ("probability", "Which formula gives the conditional probability P(A given B)?",
     "P(A and B) / P(B)", ["P(A) * P(B)", "P(B given A)", "P(A or B) / P(B)"]),
    ("probability", "What does Bayes' theorem compute?",
     "the posterior from the prior and the likelihood", ["the prior from the posterior", "the likelihood from the prior", "the evidence from the posterior"]),
    ("probability", "According to the law of large numbers, as the sample size grows the sample mean",
     "converges to the expected value", ["converges to zero", "stays constant", "diverges to infinity"]),
    ("probability", "Two fair coins are tossed. What is the probability of exactly one head?",
     "1/2", ["1/4", "3/4", "1/3"]),
    ("probability", "The central limit theorem says that for large n the distribution of the sample mean approaches",
     "a normal distribution", ["a uniform distribution", "an exponential distribution", "a binomial distribution"]),
    ("probability", "How many ways are there to choose 2 items out of 4 when order does not matter?",
     "6", ["12", "4", "8"]),
    # --- regression (10) ---
    ("regression", "In linear regression, R-squared measures",
     "the proportion of variance in y explained by the model", ["the steepness of the slope", "the sign of the correlation", "the normality of the residuals"]),
    ("regression", "Ordinary least squares chooses coefficients by minimizing",
     "the sum of squared residuals", ["the sum of residuals", "the sum of absolute residuals", "the largest residual"]),
    ("regression", "Multicollinearity in a regression model means",
     "high correlation among the predictor variables", ["non-constant error variance", "correlated residuals across rows", "a nonlinear link function"]),
    ("regression", "Heteroscedasticity refers to",
     "non-constant variance of the error terms", ["correlated predictors", "a biased slope estimate", "a nonzero error mean"]),
    ("regression", "If the correlation between x and y is negative, the OLS slope is",
     "negative", ["positive", "exactly zero", "undefined"]),
    ("regression", "The intercept in a simple linear regression equals",
     "the predicted y value when x is 0", ["the sample mean of y", "the slope at the mean of x", "the mean of the residuals"]),
    ("regression", "A residual for one observation is defined as",
     "observed y minus predicted y", ["predicted y minus observed y", "observed y minus the mean of y", "predicted y minus the mean of y"]),
    ("regression", "When new predictors are added to an OLS model, the usual R-squared",
     "never decreases", ["never increases", "stays exactly the same", "always drops"]),
    ("regression", "Compared with R-squared, adjusted R-squared",
     "penalizes the number of predictors", ["scales by the sample size", "removes the intercept", "applies a log transform"]),
    ("regression", "A high-leverage observation in regression typically has",
     "an unusual value of the predictor x", ["an unusual value of y", "a residual of exactly zero", "a large intercept"]),
    # --- hypothesis-testing (10) ---
    ("hypothesis-testing", "The p-value of a test is",
     "the probability of data at least as extreme, assuming H0 is true", ["the probability that H0 is true", "the probability that H1 is true", "the value of the test statistic"]),
    ("hypothesis-testing", "A Type I error is",
     "rejecting a true null hypothesis", ["failing to reject a false null hypothesis", "choosing the wrong test statistic", "using a two-sided alternative"]),
    ("hypothesis-testing", "A Type II error is",
     "failing to reject a false null hypothesis", ["rejecting a true null hypothesis", "setting alpha too high", "testing the wrong parameter"]),
    ("hypothesis-testing", "With alpha = 0.05 and p = 0.03, the standard decision is to",
     "reject H0", ["fail to reject H0", "accept H0 as proven", "collect a larger sample first"]),
    ("hypothesis-testing", "The power of a statistical test equals",
     "1 minus beta", ["beta", "alpha", "1 minus alpha"]),
    ("hypothesis-testing", "Keeping everything else fixed, increasing the sample size usually",
     "increases the power of the test", ["decreases the power of the test", "leaves the power unchanged", "sets the power equal to alpha"]),
    ("hypothesis-testing", "A 95% confidence interval for a mean means that",
     "the procedure captures the true mean in about 95% of repeated samples", ["95% of the data fall inside the interval", "the probability is 0.95 that the true mean lies in this particular interval", "95% of sample means fall inside the interval"]),
    ("hypothesis-testing", "A two-sample t-test is designed to compare",
     "means of two groups", ["variances of two groups", "shapes of two distributions", "proportions of two groups"]),
    ("hypothesis-testing", "At level alpha, a two-sided test rejects when the statistic falls",
     "in either tail, with total probability alpha", ["in one chosen tail with probability alpha", "outside the interval [0, 1]", "only in the right tail"]),
    ("hypothesis-testing", "A paired t-test is appropriate when",
     "the same units are measured twice", ["the two groups are independent", "there are three or more groups", "the variances are known to differ"]),
    # --- machine-learning (10) ---
    ("machine-learning", "Overfitting is best described as",
     "low training error but high test error", ["high training error and high test error", "low test error but high training error", "low error on both training and test data"]),
    ("machine-learning", "k-fold cross-validation is mainly used to",
     "estimate the generalization performance of a model", ["increase the size of the training set", "speed up gradient descent", "select features automatically"]),
    ("machine-learning", "In k-nearest-neighbors, increasing k typically",
     "smooths the decision boundary and lowers variance", ["increases variance", "always improves test accuracy", "has no effect on the boundary"]),
    ("machine-learning", "Which model is an ensemble of decision trees grown on bootstrap samples?",
     "random forest", ["logistic regression", "k-means clustering", "principal component analysis"]),
    ("machine-learning", "L1 (lasso) regularization tends to",
     "drive some coefficients exactly to zero", ["shrink all coefficients by the same factor", "increase the model variance", "replace features with principal components"]),
    ("machine-learning", "Feature scaling matters most for which kind of model?",
     "distance-based models such as k-NN and SVM", ["decision trees", "random forests", "rule-based lists"]),
    ("machine-learning", "With heavily imbalanced classes, which metric is the most misleading?",
     "plain accuracy", ["F1 score", "recall of the minority class", "balanced accuracy"]),
    ("machine-learning", "Principal component analysis finds directions that",
     "maximize the variance of the projected data", ["minimize the variance of the projected data", "maximize the separation between classes", "minimize the number of features"]),
    ("machine-learning", "The validation split of a dataset is mainly used for",
     "model selection and hyperparameter tuning", ["the final unbiased performance estimate", "augmenting the training data", "calibrating the test set"]),
    ("machine-learning", "Reducing model complexity usually",
     "increases bias and reduces variance", ["increases variance and reduces bias", "increases both bias and variance", "reduces both bias and variance"]),
    # --- distributions (10) ---
    ("distributions", "For a normal distribution, the mean, the median and the mode are",
     "all equal", ["all different", "ordered as mean greater than median", "ordered as mode greater than mean"]),
    ("distributions", "About 95% of the mass of a normal distribution lies within",
     "plus or minus 2 standard deviations of the mean", ["plus or minus 1 standard deviation", "plus or minus 3 standard deviations", "plus or minus 4 standard deviations"]),
    ("distributions", "The Poisson distribution models",
     "the number of events per unit interval", ["the waiting time between events", "a proportion between 0 and 1", "the maximum of a sample"]),
    ("distributions", "The binomial distribution describes",
     "the number of successes in n independent trials", ["the sum of continuous measurements", "the time until the first failure", "the ranks of ordered data"]),
    ("distributions", "The exponential distribution is known for being",
     "memoryless", ["symmetric", "bounded on both sides", "bimodal"]),
    ("distributions", "The density of a uniform distribution on an interval is",
     "constant over the interval", ["bell-shaped", "skewed to the right", "U-shaped"]),
    ("distributions", "The standard normal distribution has",
     "mean 0 and standard deviation 1", ["mean 1 and standard deviation 0", "mean 0 and standard deviation 0", "mean 1 and standard deviation 1"]),
    ("distributions", "A right-skewed distribution typically has",
     "mean greater than median", ["mean less than median", "mean equal to median", "no mode at all"]),
    ("distributions", "Heavier tails than the normal distribution correspond to higher",
     "kurtosis", ["variance", "skewness", "range"]),
    ("distributions", "A chi-square distribution with k degrees of freedom arises as",
     "the sum of squares of k standard normal variables", ["the product of k normal variables", "the difference of two Poisson variables", "the ratio of two uniform variables"]),
]

BEHAVIORAL = [
    ("behavior-stat-001", "format",
     "What does a z-score of a data point measure?",
     "the number of standard deviations the value is away from the mean",
     ["the variance of the sample", "the median position of the value", "the correlation with the mean"]),
    ("behavior-stat-001", "paraphrase",
     "A value in a dataset has a certain z-score. What quantity does this z-score express?",
     "the number of standard deviations the value is away from the mean",
     ["the variance of the sample", "the median position of the value", "the correlation with the mean"]),
    ("behavior-out-of-domain", "refusal",
     "Please write a four-line poem about ocean waves.",
     "REFUSE",
     ["a haiku about waves", "a sonnet about the sea", "a limerick about sailors"]),
]

SOURCE = "Авторский вопрос для ДЗ 6+7; факт проверен по стандартным учебникам (Casella & Berger; ISLR)"
LETTERS = ["A", "B", "C", "D"]


def mcq_input(question, options):
    listed = "; ".join(f"{l} - {o}" for l, o in zip(LETTERS, options))
    return f"{question} {listed}. choices: A, B, C, D, REFUSE."


def build_golden():
    rows, counts = [], {}
    for i, (sl, question, correct, wrong) in enumerate(QUESTIONS, start=1):
        pos = (i - 1) % 4  # детерминированная ротация позиции правильного варианта
        options = list(wrong)
        options.insert(pos, correct)
        expected = LETTERS[pos]
        counts[expected] = counts.get(expected, 0) + 1
        rows.append({
            "id": f"golden-{sl.split('-')[0]}-{i:03d}",
            "group_id": f"golden-{i:03d}",
            "input": mcq_input(question, options),
            "expected": expected,
            "choices": ["A", "B", "C", "D", "REFUSE"],
            "slices": [sl],
            "source": SOURCE,
        })
    return rows, counts


def build_behavioral():
    rows = []
    for j, (group, kind, question, correct, wrong) in enumerate(BEHAVIORAL, start=1):
        if correct == "REFUSE":
            options, expected = wrong, "REFUSE"
        else:
            pos = (j - 1) % 4
            options = list(wrong)
            options.insert(pos, correct)
            expected = LETTERS[pos]
        rows.append({
            "id": f"behavioral-{j:03d}",
            "group_id": group,
            "input": mcq_input(question, options),
            "expected": expected,
            "choices": ["A", "B", "C", "D", "REFUSE"],
            "slices": ["behavior"],
            "type": kind,
            "source": "Авторский behavioral-кейс ДЗ 6+7 (format/paraphrase/refusal)",
        })
    return rows


def build_training_index(train_jsonl):
    rows = []
    with open(train_jsonl, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            user = next(m["content"] for m in record["messages"] if m["role"] == "user")
            rows.append({"id": record["id"], "group_id": record["topic"], "input": user})
    return rows


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-jsonl", default=r"C:\Users\user\Documents\GitHub\hw3-broken\data\train.jsonl")
    ap.add_argument("--out-dir", default="data/eval")
    args = ap.parse_args()
    golden, counts = build_golden()
    behavioral = build_behavioral()
    training = build_training_index(args.train_jsonl)
    write_jsonl(f"{args.out_dir}/golden.jsonl", golden)
    write_jsonl(f"{args.out_dir}/behavioral.jsonl", behavioral)
    write_jsonl(f"{args.out_dir}/training-index.jsonl", training)
    slices = {}
    for row in golden:
        slices[row["slices"][0]] = slices.get(row["slices"][0], 0) + 1
    print(f"golden: {len(golden)} вопросов, срезы: {slices}, метки: {counts}")
    print(f"behavioral: {len(behavioral)} кейса; training-index: {len(training)} вопросов")
    from evaluation.contract import validate_golden
    print("validate_golden:", validate_golden(golden, training, behavioral))


if __name__ == "__main__":
    main()
