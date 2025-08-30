using System;
using System.Threading;
using System.Threading.Tasks;
using VRChatProximityApp.Models;

namespace VRChatProximityApp.Services
{
    public class VRChatOSCService : IDisposable
    {
        private readonly int _oscPort;
        private CancellationTokenSource? _cancellationTokenSource;
        private bool _isRunning = false;
        
        public event EventHandler<VRChatUser>? UserPositionUpdated;
        public event EventHandler<string>? PlayerPositionUpdated;
        public event EventHandler<bool>? ConnectionStatusChanged;

        public Vector3 PlayerPosition { get; private set; }
        public bool IsConnected => _isRunning;

        public VRChatOSCService(int port = 9001)
        {
            _oscPort = port;
        }

        public async Task StartAsync()
        {
            if (_isRunning) return;

            try
            {
                _cancellationTokenSource = new CancellationTokenSource();
                
                _isRunning = true;
                ConnectionStatusChanged?.Invoke(this, true);
                
                // For now, simulate OSC connection without actual OSC receiver
                // due to compatibility issues with Rug.Osc on .NET 9
                await Task.Run(() => SimulateOscMessages(_cancellationTokenSource.Token));
            }
            catch (Exception ex)
            {
                _isRunning = false;
                ConnectionStatusChanged?.Invoke(this, false);
                throw new InvalidOperationException($"Failed to start VRChat OSC service: {ex.Message}", ex);
            }
        }

        public void Stop()
        {
            if (!_isRunning) return;

            _isRunning = false;
            _cancellationTokenSource?.Cancel();
            
            _cancellationTokenSource?.Dispose();
            _cancellationTokenSource = null;
            
            ConnectionStatusChanged?.Invoke(this, false);
        }

        private async Task SimulateOscMessages(CancellationToken cancellationToken)
        {
            var random = new Random();
            
            while (!cancellationToken.IsCancellationRequested && _isRunning)
            {
                try
                {
                    // Simulate player movement for demo purposes
                    var time = DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
                    var x = (float)(Math.Sin(time * 0.1) * 5);
                    var z = (float)(Math.Cos(time * 0.1) * 5);
                    
                    PlayerPosition = new Vector3(x, 0, z);
                    PlayerPositionUpdated?.Invoke(this, "/tracking/head/position");
                    
                    await Task.Delay(100, cancellationToken); // Update every 100ms
                }
                catch (TaskCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in OSC simulation: {ex.Message}");
                    await Task.Delay(1000, cancellationToken); // Wait before retrying
                }
            }
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
