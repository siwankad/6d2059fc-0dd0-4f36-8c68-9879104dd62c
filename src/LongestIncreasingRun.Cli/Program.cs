using System;

using LongestIncreasingRun;

if (args.Length > 1)
{
    Console.Error.WriteLine("Usage: LongestIncreasingRun.Cli [sequence]");
    Console.Error.WriteLine("Omit the sequence to be prompted for strings.");
    return 1;
}

if (args.Length == 1)
{
    Console.WriteLine(LongestIncreasingRunFinder.Find(args[0]));
    return 0;
}

while (true)
{
    Console.Error.Write("Enter the string: ");
    string? line = Console.ReadLine();
    if (line is null)
    {
        return 0;
    }

    string result = LongestIncreasingRunFinder.Find(line);
    if (result == LongestIncreasingRunFinder.InvalidInputMessage)
    {
        Console.WriteLine(result);
    }
    else
    {
        Console.WriteLine("Longest increasing subsequence is: " + result);
    }
    Console.WriteLine("\n");
}
