# Shared test prompts for math agents
# Each item can be either a string (question only) or a dict with 'question' and optional 'answer'
TEST_PROMPTS = [
    {
        "question": """In one state, 52% of the voters are Republicans, and 48% are Democrats. In a second state, 47% of the voters are Republicans, and 53% are Democrats. Suppose a simple random sample of 100 voters are surveyed from each state.

What is the probability that the survey will show a greater percentage of Republican voters in the second state than in the first state?

(A) 0.04

(B) 0.05

(C) 0.24

(D) 0.71

(E) 0.76""",
        "answer": """The correct answer is C. For this analysis, let P1 = the proportion of Republican voters in the first state, P2 = the proportion of Republican voters in the second state, p1 = the proportion of Republican voters in the sample from the first state, and p2 = the proportion of Republican voters in the sample from the second state. The number of voters sampled from the first state (n1) = 100, and the number of voters sampled from the second state (n2) = 100.

The solution involves four steps.

Make sure the sample size is big enough to model differences with a normal population. Because n1P1 = 100 * 0.52 = 52, n1(1 - P1) = 100 * 0.48 = 48, n2P2 = 100 * 0.47 = 47, and n2(1 - P2) = 100 * 0.53 = 53 are each greater than 10, the sample size is large enough.
Find the mean of the difference in sample proportions: E(p1 - p2) = P1 - P2 = 0.52 - 0.47 = 0.05.
Find the standard deviation of the difference.
σd = sqrt{ [ P1(1 - P1) / n1 ] + [ P2(1 - P2) / n2 ] }

σd = sqrt{ [ (0.52)(0.48) / 100 ] + [ (0.47)(0.53) / 100 ] }

σd = sqrt (0.002496 + 0.002491) = sqrt(0.004987) = 0.0706

Find the probability. This problem requires us to find the probability that p1 is less than p2. This is equivalent to finding the probability that p1 - p2 is less than zero. To find this probability, we need to transform the random variable (p1 - p2) into a z-score. That transformation appears below.
zp1 - p2 = (x - μp1 - p2 ) / σd = (0 - 0.05)/0.0706 = -0.7082

Using Stat Trek's Normal Distribution Calculator, we find that the probability of a z-score being -0.7082 or less is 0.24.

Therefore, the probability that the survey will show a greater percentage of Republican voters in the second state than in the first state is 0.24."""
    },
    {
        "question": "A card is drawn randomly from a deck of ordinary playing cards. You win $10 if the card is a spade or an ace. What is the probability that you will win the game?",
        "answer": """Let S = the event that the card is a spade; and let A = the event that the card is an ace. You will win the game if either of these two events occur. Therefore, this problem requires you to find the probability of the union of two events.

We know the following:

There are 52 cards in the deck.
There are 13 spades, so P(S) = 13/52.
There are 4 aces, so P(A) = 4/52.
There is 1 ace that is also a spade, so P(S ∩ A) = 1/52.
Therefore, based on the rule of addition:

P(S ∪ A) = P(S) + P(A) - P(S ∩ A)
P(S ∪ A) = 13/52 + 4/52 - 1/52 = 16/52 = 4/13"""
    },
    {
        "question": "The probability that a student is accepted to a prestigious college is 0.3. If 5 students from the same school apply, what is the probability that at most 2 are accepted?",
        "answer": """To solve this problem, we compute 3 individual probabilities, using the binomial formula. The sum of all these probabilities is the answer we seek. Thus,

b(x < 2; 5, 0.3) = b(x = 0; 5, 0.3) + b(x = 1; 5, 0.3) + b(x = 2; 5, 0.3)
b(x < 2; 5, 0.3) = 0.1681 + 0.3601 + 0.3087
b(x < 2; 5, 0.3) = 0.8369"""
    },
    {
        "question": "How many different ways can you arrange the letters X, Y, and Z?",
        "answer": """One way to solve this problem is to list all of the possible permutations of X, Y, and Z. They are: XYZ, XZY, YXZ, YZX, ZXY, and ZYX. Thus, there are 6 possible permutations.

Another approach is to use the formula for counting permutations. That formula appears below.

How to count permutations. The number of permutations of nobjects taken r at a time is:
nPr = n(n - 1)(n - 2) ... (n - r + 1) = n! / (n - r)!
The above formula tells us that the number of permutations is n! / (n - r)!. We have 3 distinct objects (the letters X, Y, and Z) so n = 3. And we want to arrange them in groups of 3, so r = 3. Thus, the number of permutations is 3! / (3 - 3)! or 3! / 0!. This is equal to (3)(2)(1)/1 = 6."""
    }
]