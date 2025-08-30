using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Threading;
using VRChatProximityApp.Models;

namespace VRChatProximityApp.Services
{
    public class ProximityService : INotifyPropertyChanged, IDisposable
    {
        private readonly VRChatOSCService _oscService;
        private readonly VRChatLogService _logService;
        private readonly Timer _updateTimer;
        private readonly Dispatcher _dispatcher;
        
        private double _sightDistance = 10.0; // Default sight distance in meters
        private bool _isEnabled = false;
        private Vector3 _playerPosition;
        private bool _useRealUsers = true;

        public ObservableCollection<VRChatUser> AllUsers { get; } = new();
        public ObservableCollection<VRChatUser> VisibleUsers { get; } = new();

        public double SightDistance
        {
            get => _sightDistance;
            set
            {
                if (SetProperty(ref _sightDistance, Math.Max(0.1, Math.Min(100.0, value))))
                {
                    UpdateVisibleUsers();
                }
            }
        }

        public bool IsEnabled
        {
            get => _isEnabled;
            set => SetProperty(ref _isEnabled, value);
        }

        public Vector3 PlayerPosition
        {
            get => _playerPosition;
            private set => SetProperty(ref _playerPosition, value);
        }

        public bool IsConnected => _oscService.IsConnected;

        public event PropertyChangedEventHandler? PropertyChanged;
        public event EventHandler<VRChatUser>? UserVisibilityChanged;

        public bool UseRealUsers
        {
            get => _useRealUsers;
            set => SetProperty(ref _useRealUsers, value);
        }

        public ProximityService()
        {
            _dispatcher = Dispatcher.CurrentDispatcher;
            
            // Initialize OSC service for player position
            _oscService = new VRChatOSCService();
            _oscService.PlayerPositionUpdated += OnPlayerPositionUpdated;
            _oscService.ConnectionStatusChanged += OnConnectionStatusChanged;
            
            // Initialize log service for user detection
            _logService = new VRChatLogService();
            _logService.UserJoined += OnUserJoined;
            _logService.UserLeft += OnUserLeft;
            _logService.WorldChanged += OnWorldChanged;
            
            // Update every 100ms for smooth proximity detection
            _updateTimer = new Timer(UpdateProximity, null, Timeout.Infinite, 100);
        }

        public async Task StartAsync()
        {
            try
            {
                // Start VRChat log monitoring for real users
                try
                {
                    await _logService.StartAsync();
                    UseRealUsers = true;
                }
                catch (Exception logEx)
                {
                    Console.WriteLine($"Failed to start VRChat log service: {logEx.Message}");
                    Console.WriteLine("Falling back to demo mode...");
                    UseRealUsers = false;
                    AddDemoUsers();
                }
                
                // Start OSC service for player position
                await _oscService.StartAsync();
                
                _updateTimer.Change(0, 100); // Start the update timer
                IsEnabled = true;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to start proximity service: {ex.Message}", ex);
            }
        }

        public void Stop()
        {
            _updateTimer.Change(Timeout.Infinite, Timeout.Infinite);
            _oscService.Stop();
            _logService.Stop();
            IsEnabled = false;
            
            _dispatcher.Invoke(() =>
            {
                AllUsers.Clear();
                VisibleUsers.Clear();
            });
        }

        private void OnPlayerPositionUpdated(object? sender, string address)
        {
            PlayerPosition = _oscService.PlayerPosition;
        }

        private void OnConnectionStatusChanged(object? sender, bool isConnected)
        {
            OnPropertyChanged(nameof(IsConnected));
        }
        
        private void OnUserJoined(object? sender, VRChatUser user)
        {
            AddUser(user);
        }
        
        private void OnUserLeft(object? sender, string userId)
        {
            RemoveUser(userId);
        }
        
        private void OnWorldChanged(object? sender, string worldName)
        {
            _dispatcher.Invoke(() =>
            {
                // Clear all users when changing worlds
                AllUsers.Clear();
                VisibleUsers.Clear();
            });
        }

        private void UpdateProximity(object? state)
        {
            if (!IsEnabled) return;

            _dispatcher.BeginInvoke(() =>
            {
                UpdateVisibleUsers();
            });
        }

        private void UpdateVisibleUsers()
        {
            foreach (var user in AllUsers)
            {
                var distance = PlayerPosition.DistanceTo(user.Position);
                user.DistanceFromPlayer = distance;
                
                var shouldBeVisible = distance <= SightDistance;
                
                if (user.IsVisible != shouldBeVisible)
                {
                    user.IsVisible = shouldBeVisible;
                    UserVisibilityChanged?.Invoke(this, user);
                    
                    if (shouldBeVisible && !VisibleUsers.Contains(user))
                    {
                        VisibleUsers.Add(user);
                    }
                    else if (!shouldBeVisible && VisibleUsers.Contains(user))
                    {
                        VisibleUsers.Remove(user);
                    }
                }
            }
        }

        public void AddUser(VRChatUser user)
        {
            _dispatcher.Invoke(() =>
            {
                if (!AllUsers.Any(u => u.UserId == user.UserId))
                {
                    AllUsers.Add(user);
                }
            });
        }

        public void RemoveUser(string userId)
        {
            _dispatcher.Invoke(() =>
            {
                var user = AllUsers.FirstOrDefault(u => u.UserId == userId);
                if (user != null)
                {
                    AllUsers.Remove(user);
                    VisibleUsers.Remove(user);
                }
            });
        }

        public void UpdateUserPosition(string userId, Vector3 position)
        {
            _dispatcher.Invoke(() =>
            {
                var user = AllUsers.FirstOrDefault(u => u.UserId == userId);
                if (user != null)
                {
                    user.Position = position;
                    user.LastSeen = DateTime.Now;
                    user.IsConnected = true;
                }
            });
        }

        // Demo method - remove in production
        private void AddDemoUsers()
        {
            var random = new Random();
            
            for (int i = 1; i <= 10; i++)
            {
                var user = new VRChatUser
                {
                    UserId = $"user_{i}",
                    DisplayName = $"Demo User {i}",
                    Position = new Vector3(
                        (float)(random.NextDouble() - 0.5) * 30, // -15 to 15
                        0,
                        (float)(random.NextDouble() - 0.5) * 30  // -15 to 15
                    ),
                    IsConnected = true
                };
                
                AddUser(user);
            }
        }

        protected bool SetProperty<T>(ref T backingStore, T value, [CallerMemberName] string propertyName = "")
        {
            if (EqualityComparer<T>.Default.Equals(backingStore, value))
                return false;

            backingStore = value;
            OnPropertyChanged(propertyName);
            return true;
        }

        protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void Dispose()
        {
            _updateTimer?.Dispose();
            _oscService?.Dispose();
            _logService?.Dispose();
        }
    }
}
