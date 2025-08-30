using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using VRChatProximityApp.Models;

namespace VRChatProximityApp.Services
{
    public class VRChatLogService : IDisposable
    {
        private FileSystemWatcher? _logWatcher;
        private readonly string _vrchatLogPath;
        private bool _isRunning = false;
        private CancellationTokenSource? _cancellationTokenSource;
        
        // Regex patterns for VRChat log parsing
        private static readonly Regex UserJoinPattern = new Regex(
            @"\[Behaviour\] OnPlayerJoined (.*)", 
            RegexOptions.Compiled | RegexOptions.IgnoreCase);
            
        private static readonly Regex UserLeftPattern = new Regex(
            @"\[Behaviour\] OnPlayerLeft (.*)", 
            RegexOptions.Compiled | RegexOptions.IgnoreCase);
            
        private static readonly Regex WorldChangePattern = new Regex(
            @"Joining or Creating Room: (.*)", 
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        public event EventHandler<VRChatUser>? UserJoined;
        public event EventHandler<string>? UserLeft;
        public event EventHandler<string>? WorldChanged;
        public event EventHandler<bool>? ConnectionStatusChanged;

        public bool IsConnected => _isRunning;

        public VRChatLogService()
        {
            // VRChat log file location
            var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            _vrchatLogPath = Path.Combine(localAppData + "Low", "VRChat", "VRChat");
        }

        public async Task StartAsync()
        {
            if (_isRunning) return;

            try
            {
                if (!Directory.Exists(_vrchatLogPath))
                {
                    throw new DirectoryNotFoundException($"VRChat log directory not found: {_vrchatLogPath}");
                }

                _cancellationTokenSource = new CancellationTokenSource();
                
                // Set up file system watcher for new log files
                _logWatcher = new FileSystemWatcher(_vrchatLogPath)
                {
                    Filter = "output_log_*.txt",
                    NotifyFilter = NotifyFilters.CreationTime | NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };

                _logWatcher.Changed += OnLogFileChanged;
                _logWatcher.Created += OnLogFileChanged;

                _isRunning = true;
                ConnectionStatusChanged?.Invoke(this, true);

                // Start reading existing log file
                await Task.Run(() => ReadExistingLogFile(_cancellationTokenSource.Token));
            }
            catch (Exception ex)
            {
                _isRunning = false;
                ConnectionStatusChanged?.Invoke(this, false);
                throw new InvalidOperationException($"Failed to start VRChat log service: {ex.Message}", ex);
            }
        }

        public void Stop()
        {
            if (!_isRunning) return;

            _isRunning = false;
            _cancellationTokenSource?.Cancel();
            
            if (_logWatcher != null)
            {
                _logWatcher.Changed -= OnLogFileChanged;
                _logWatcher.Created -= OnLogFileChanged;
                _logWatcher.EnableRaisingEvents = false;
                _logWatcher.Dispose();
                _logWatcher = null;
            }
            
            _cancellationTokenSource?.Dispose();
            _cancellationTokenSource = null;
            
            ConnectionStatusChanged?.Invoke(this, false);
        }

        private void OnLogFileChanged(object sender, FileSystemEventArgs e)
        {
            if (!_isRunning) return;
            
            Task.Run(() => ProcessLogFile(e.FullPath));
        }

        private void ReadExistingLogFile(CancellationToken cancellationToken)
        {
            try
            {
                var latestLogFile = GetLatestLogFile();
                if (latestLogFile != null)
                {
                    ProcessLogFile(latestLogFile);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error reading existing log file: {ex.Message}");
            }
        }

        private string? GetLatestLogFile()
        {
            try
            {
                var logFiles = Directory.GetFiles(_vrchatLogPath, "output_log_*.txt")
                    .OrderByDescending(f => File.GetLastWriteTime(f))
                    .ToArray();
                    
                return logFiles.FirstOrDefault();
            }
            catch
            {
                return null;
            }
        }

        private async void ProcessLogFile(string filePath)
        {
            try
            {
                using var fileStream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
                using var reader = new StreamReader(fileStream);
                
                // Move to end of file to read new entries
                reader.BaseStream.Seek(0, SeekOrigin.End);
                
                string? line;
                while ((line = await reader.ReadLineAsync()) != null && _isRunning)
                {
                    ProcessLogLine(line);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing log file {filePath}: {ex.Message}");
            }
        }

        private void ProcessLogLine(string line)
        {
            if (string.IsNullOrEmpty(line)) return;

            try
            {
                // Check for user join
                var joinMatch = UserJoinPattern.Match(line);
                if (joinMatch.Success)
                {
                    var username = joinMatch.Groups[1].Value.Trim();
                    var user = new VRChatUser
                    {
                        UserId = GenerateUserIdFromName(username),
                        DisplayName = username,
                        Position = GenerateRandomPosition(), // We can't get actual position from logs
                        IsConnected = true,
                        LastSeen = DateTime.Now
                    };
                    UserJoined?.Invoke(this, user);
                    return;
                }

                // Check for user left
                var leftMatch = UserLeftPattern.Match(line);
                if (leftMatch.Success)
                {
                    var username = leftMatch.Groups[1].Value.Trim();
                    var userId = GenerateUserIdFromName(username);
                    UserLeft?.Invoke(this, userId);
                    return;
                }

                // Check for world change
                var worldMatch = WorldChangePattern.Match(line);
                if (worldMatch.Success)
                {
                    var worldName = worldMatch.Groups[1].Value.Trim();
                    WorldChanged?.Invoke(this, worldName);
                    return;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing log line: {ex.Message}");
            }
        }

        private string GenerateUserIdFromName(string username)
        {
            // Create a consistent user ID from username
            return $"user_{username.GetHashCode():X}";
        }

        private Vector3 GenerateRandomPosition()
        {
            // Generate a random position since we can't get actual positions from logs
            var random = new Random();
            return new Vector3(
                (float)(random.NextDouble() - 0.5) * 20, // -10 to 10
                0,
                (float)(random.NextDouble() - 0.5) * 20  // -10 to 10
            );
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
