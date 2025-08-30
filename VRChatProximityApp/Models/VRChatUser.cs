using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace VRChatProximityApp.Models
{
    public class VRChatUser : INotifyPropertyChanged
    {
        private string _displayName = string.Empty;
        private string _userId = string.Empty;
        private Vector3 _position;
        private bool _isVisible = true;
        private double _distanceFromPlayer = 0;
        private DateTime _lastSeen = DateTime.Now;
        private bool _isConnected = false;

        public string DisplayName
        {
            get => _displayName;
            set => SetProperty(ref _displayName, value);
        }

        public string UserId
        {
            get => _userId;
            set => SetProperty(ref _userId, value);
        }

        public Vector3 Position
        {
            get => _position;
            set => SetProperty(ref _position, value);
        }

        public bool IsVisible
        {
            get => _isVisible;
            set => SetProperty(ref _isVisible, value);
        }

        public double DistanceFromPlayer
        {
            get => _distanceFromPlayer;
            set => SetProperty(ref _distanceFromPlayer, value);
        }

        public DateTime LastSeen
        {
            get => _lastSeen;
            set => SetProperty(ref _lastSeen, value);
        }

        public bool IsConnected
        {
            get => _isConnected;
            set => SetProperty(ref _isConnected, value);
        }

        public event PropertyChangedEventHandler? PropertyChanged;

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
    }

    public struct Vector3
    {
        public float X { get; set; }
        public float Y { get; set; }
        public float Z { get; set; }

        public Vector3(float x, float y, float z)
        {
            X = x;
            Y = y;
            Z = z;
        }

        public double DistanceTo(Vector3 other)
        {
            var dx = X - other.X;
            var dy = Y - other.Y;
            var dz = Z - other.Z;
            return Math.Sqrt(dx * dx + dy * dy + dz * dz);
        }

        public override string ToString()
        {
            return $"({X:F2}, {Y:F2}, {Z:F2})";
        }
    }
}
