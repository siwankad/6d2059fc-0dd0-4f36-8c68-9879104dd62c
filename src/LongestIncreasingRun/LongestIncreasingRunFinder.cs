using System.Globalization;
using System.Text;

namespace LongestIncreasingRun;

/// <summary>
/// Finds the earliest longest strictly increasing run.
/// </summary>
/// <remarks>
/// A run is a contiguous stretch of the input. It is strictly increasing when
/// each value is greater than the value immediately before it. The difference
/// may be any positive amount.
///
/// Those runs are already separated by the places where the next value does
/// not increase, so one left-to-right pass finds every maximal run. The answer
/// is the longest. When two runs share that length, the one that starts earlier
/// is kept: a new run replaces the best run only when it is strictly longer.
///
/// The pass is O(n) in time. Parsing stores the integers, which is O(n) space.
/// The search itself keeps only a handful of indexes.
/// </remarks>
public static class LongestIncreasingRunFinder
{
    /// <summary>
    /// Returns the earliest longest strictly increasing run as one
    /// space-separated string. A single value has no separator.
    /// </summary>
    /// <param name="input">
    /// Integers separated by a single space, for example <c>6 1 5 9 2</c>.
    /// </param>
    public static string Find(string input)
    {
        ArgumentNullException.ThrowIfNull(input);

        int[] values = Parse(input);
        Run run = SelectEarliestLongestRun(values);
        return Format(values, run);
    }

    private readonly record struct Run(int Start, int Length);

    private static int[] Parse(string input)
    {
        if (input.Length == 0)
        {
            return [];
        }

        string[] tokens = input.Split(' ');
        var values = new int[tokens.Length];
        for (int index = 0; index < tokens.Length; index++)
        {
            values[index] = int.Parse(tokens[index], CultureInfo.InvariantCulture);
        }

        return values;
    }

    private static Run SelectEarliestLongestRun(int[] values)
    {
        if (values.Length == 0)
        {
            return new Run(0, 0);
        }

        // A single value is a run of length 1, so the best run starts there
        // until a longer one is found.
        int bestStart = 0;
        int bestLength = 1;
        int runStart = 0;

        for (int index = 1; index < values.Length; index++)
        {
            if (values[index] > values[index - 1])
            {
                continue;
            }

            // index is the first value that does not extend the current run.
            int length = index - runStart;
            if (length > bestLength)
            {
                bestStart = runStart;
                bestLength = length;
            }

            runStart = index;
        }

        // The final run never sees a following value, so it is closed here.
        int closingLength = values.Length - runStart;
        if (closingLength > bestLength)
        {
            bestStart = runStart;
            bestLength = closingLength;
        }

        return new Run(bestStart, bestLength);
    }

    private static string Format(int[] values, Run run)
    {
        if (run.Length == 0)
        {
            return string.Empty;
        }

        var builder = new StringBuilder();
        int end = run.Start + run.Length;
        for (int index = run.Start; index < end; index++)
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
