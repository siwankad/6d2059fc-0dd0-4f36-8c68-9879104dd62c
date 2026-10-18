# Longest strictly increasing run

A C# function on .NET 10. It takes one string of integers separated by single spaces and returns the earliest longest strictly increasing run.

Start with `src/LongestIncreasingRun/LongestIncreasingRunFinder.cs`, method `Find`.

## The result is a run, not a subsequence that skips values

Input:

```text
6 2 4 6 1 5 9 2
```

Two contiguous stretches have length 3:

| Indexes | Run     | Why it is or is not returned      |
| ------- | ------- | --------------------------------- |
| 1–3     | `2 4 6` | Length 3, and it starts first     |
| 4–6     | `1 5 9` | Same length, but it starts later  |

The returned string is `2 4 6`.

`2 4 5 9` and `2 4 6 9` are longer, and both skip a value that sits between the chosen numbers. They are not runs, so they are not returned. The same rule gives `1 5 9` for `6 1 5 9 2`, because that run is the longest one in that input.

## Algorithm

A strictly increasing run is a contiguous stretch where each value is greater than the value immediately before it. The step can be any positive amount. An equal neighbour ends the run.

Those stretches are already split by the places where the sequence fails to increase. One left-to-right pass finds all of them:

1. Parse the string into integers. Comparison is numeric, so `-5 -1 0 4` increases and `9` is not greater than `10` just because it has fewer digits.
2. Walk the integers once. While each value is greater than the previous one, the current run continues.
3. When the next value is less than or equal to the current one, close the run. Keep it only when it is **strictly longer** than the best run seen so far. An equal length does not replace the best run, so the earlier start wins.
4. Close the final run after the loop. It has no following value that would close it inside the loop.
5. Write the chosen integers back out, separated by a single space, with no leading or trailing whitespace.

The search does `n - 1` comparisons. Every value has to be read: an unread value could extend a run or start a longer one. The pass is therefore linear, which matches the lower bound. Parsing stores the integers, so the array is proportional to the input. The search itself keeps a few indexes.

If an interviewer asks for extra memory that does not grow with the input, the same pass can remember the character span of the best run and return that slice of the original string. The indexes are a handful of integers. The array form is the one in `Find`, because the steps are easier to point at while explaining the tie.

This is the contiguous problem. The classic longest increasing subsequence, which may skip values, is a different problem and uses an `O(n log n)` search. That search fails the example above.

## Walk the tie by hand

`6 2 4 6 1 5 9 2`

- `6` starts a run of length 1.
- `2` does not increase, so that run closes at length 1. A new run starts at `2`.
- `4` and `6` extend it. The run is `2 4 6`, length 3.
- `1` does not increase. Length 3 replaces the earlier length 1.
- `5` and `9` build `1 5 9`, also length 3. Equal length does not replace `2 4 6`.
- `2` closes that run. The last value is a run of length 1.

The result is `2 4 6`.

## Project layout

| Path | Role |
| --- | --- |
| `src/LongestIncreasingRun/LongestIncreasingRunFinder.cs` | The function under test: `LongestIncreasingRunFinder.Find` |
| `src/LongestIncreasingRun.Cli` | Thin console wrapper, used by the container |
| `tests/LongestIncreasingRun.Tests/RunRulesTests.cs` | The rules, one readable case at a time, plus a slow scan used as an oracle |
| `tests/LongestIncreasingRun.Tests/AcceptanceFixtureTests.cs` | AT-01 through AT-11 and RC-01 through RC-08 |
| `Downloads/acceptance-fixtures.json` | The exact inputs, expected strings, and SHA-256 digests |

`Find` takes one string and needs no second argument. Supporting parsing and formatting stay private.

## Verify

Install the .NET SDK 10. The repository pins SDK `10.0.402` in `global.json` and allows a newer 10.x SDK.

From the repository root:

```bash
dotnet restore max-run.slnx
dotnet build max-run.slnx
dotnet test max-run.slnx
```

`dotnet build` is expected to finish with no compiler warnings. Warnings are treated as errors.

Try the first published case from the console:

```bash
dotnet run --project src/LongestIncreasingRun.Cli -- "6 1 5 9 2"
```

That prints `1 5 9`.

## Coverage

`coverlet.collector` writes a Cobertura report for the `LongestIncreasingRun` assembly. The report is the output of the same run that executes AT-01 through AT-11.

```bash
dotnet test max-run.slnx -c Release --settings coverage.runsettings --collect:"XPlat Code Coverage" --results-directory ./coverage
```

The report is `./coverage/<guid>/coverage.cobertura.xml`. With the tests in this repository, that report shows full line and branch coverage of `LongestIncreasingRunFinder`.

## Lint

EditorConfig is at the repository root. The check is:

```bash
dotnet format max-run.slnx --verify-no-changes
```

A clean tree prints that no files were formatted and exits 0.

## Docker

The SDK image is `mcr.microsoft.com/dotnet/sdk:10.0`. The runtime image is `mcr.microsoft.com/dotnet/runtime:10.0`.

Run the unit tests while building the test stage:

```bash
docker build --target test -t longest-increasing-run:test .
```

Build the console image and run a published case:

```bash
docker build -t longest-increasing-run .
docker run --rm longest-increasing-run "6 2 4 6 1 5 9 2"
```

That prints `2 4 6`.

## Continuous integration

`.github/workflows/ci.yml` runs on every push, including a push to the default branch. It restores, runs `dotnet format --verify-no-changes`, runs the unit tests with coverage, and uploads the coverage directory.

## Requirements baseline

The exercise brief is `source/code-test.md`. The acceptance baseline, with the pass and fail criteria, is `Downloads/Longest-Increasing-Subsequence-Requirements.pdf`. The fixture file beside that PDF is the file the tests load.
