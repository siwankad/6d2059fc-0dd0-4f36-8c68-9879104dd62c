using System.Globalization;
using System.Text;

namespace LongestIncreasingRun.Tests;

/// <summary>
/// Small cases that make each rule visible without opening the fixture file.
/// The same inputs are also checked, by id, in <see cref="AcceptanceFixtureTests"/>.
/// </summary>
public sealed class RunRulesTests
{
    [Fact]
    public void OneValueIsAlreadyARun()
    {
        Assert.Equal("42", LongestIncreasingRunFinder.Find("42"));
    }

    [Fact]
    public void StrictlyIncreasingInputIsReturnedUnchanged()
    {
        Assert.Equal("1 2 3 4", LongestIncreasingRunFinder.Find("1 2 3 4"));
    }

    [Fact]
    public void StrictlyDecreasingInputReturnsTheFirstValue()
    {
        Assert.Equal("9", LongestIncreasingRunFinder.Find("9 7 5 3"));
    }

    [Fact]
    public void EqualLengthRunsReturnTheEarlierStart()
    {
        Assert.Equal("1 3", LongestIncreasingRunFinder.Find("1 3 2 4"));
    }

    [Fact]
    public void PublishedTieReturnsTheContiguousRunThatStartsFirst()
    {
        // 2 4 6 and 1 5 9 both have length 3. Skipping values to build
        // 2 4 5 9 or 2 4 6 9 is not a run.
        Assert.Equal("2 4 6", LongestIncreasingRunFinder.Find("6 2 4 6 1 5 9 2"));
    }

    [Fact]
    public void EqualNeighbourEndsTheRun()
    {
        Assert.Equal("1 2", LongestIncreasingRunFinder.Find("1 2 2 3"));
    }

    [Fact]
    public void AnyPositiveStepCountsAsAnIncrease()
    {
        Assert.Equal("1 100 101", LongestIncreasingRunFinder.Find("1 100 101"));
    }

    [Fact]
    public void ZeroAndNegativeValuesCompareNumerically()
    {
        Assert.Equal("-5 -1 0 4", LongestIncreasingRunFinder.Find("-5 -1 0 4 1"));
    }

    [Fact]
    public void ALaterShorterRunIsIgnored()
    {
        Assert.Equal("1 2 3", LongestIncreasingRunFinder.Find("1 2 3 0 1"));
    }

    [Fact]
    public void FirstPublishedExampleReturnsOneFiveNine()
    {
        Assert.Equal("1 5 9", LongestIncreasingRunFinder.Find("6 1 5 9 2"));
    }

    [Fact]
    public void EmptyInputIsRejectedWithAMessage()
    {
        Assert.Equal(LongestIncreasingRunFinder.InvalidInputMessage, LongestIncreasingRunFinder.Find(string.Empty));
    }

    [Fact]
    public void NullInputIsRejected()
    {
        Assert.Throws<ArgumentNullException>(() => LongestIncreasingRunFinder.Find(null!));
    }

    [Fact]
    public void LettersAreRejectedWithAMessage()
    {
        Assert.Equal(LongestIncreasingRunFinder.InvalidInputMessage, LongestIncreasingRunFinder.Find("abc"));
    }

    [Fact]
    public void ALetterAmongNumbersIsRejectedWithAMessage()
    {
        Assert.Equal(LongestIncreasingRunFinder.InvalidInputMessage, LongestIncreasingRunFinder.Find("6 1 a 9"));
    }

    [Fact]
    public void AValueOutsideInt32IsRejectedWithAMessage()
    {
        Assert.Equal(LongestIncreasingRunFinder.InvalidInputMessage, LongestIncreasingRunFinder.Find("6 9999999999 2"));
    }

    [Fact]
    public void LinearScanMatchesABruteForceScan()
    {
        var random = new Random(20261017);
        for (int trial = 0; trial < 200; trial++)
        {
            int length = random.Next(1, 32);
            var values = new int[length];
            for (int index = 0; index < values.Length; index++)
            {
                values[index] = random.Next(-30, 50);
            }

            string input = string.Join(
                ' ',
                values.Select(value => value.ToString(CultureInfo.InvariantCulture)));

            Assert.Equal(SlowEarliestLongestRun(values), LongestIncreasingRunFinder.Find(input));
        }
    }

    /// <summary>
    /// Checks every maximal run from left to right. This is the rule the linear
    /// scan is supposed to implement, written the slow way on purpose.
    /// </summary>
    private static string SlowEarliestLongestRun(int[] values)
    {
        int bestStart = 0;
        int bestLength = 0;
        for (int start = 0; start < values.Length; start++)
        {
            int end = start;
            while (end + 1 < values.Length && values[end + 1] > values[end])
            {
                end++;
            }

            int length = end - start + 1;
            if (length > bestLength)
            {
                bestStart = start;
                bestLength = length;
            }
        }

        var builder = new StringBuilder();
        for (int index = bestStart; index < bestStart + bestLength; index++)
        {
            if (builder.Length > 0)
            {
                builder.Append(' ');
            }

            builder.Append(values[index].ToString(CultureInfo.InvariantCulture));
        }

        return builder.ToString();
    }
}
