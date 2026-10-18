using LongestIncreasingRun;

if (args.Length > 1)
{
    Console.Error.WriteLine("Usage: LongestIncreasingRun.Cli [sequence]");
    Console.Error.WriteLine("Omit the sequence to read it from standard input.");
    return 1;
}

string input = args.Length == 1
    ? args[0]
    : Console.In.ReadToEnd().TrimEnd('\r', '\n');

Console.WriteLine(LongestIncreasingRunFinder.Find(input));
return 0;
