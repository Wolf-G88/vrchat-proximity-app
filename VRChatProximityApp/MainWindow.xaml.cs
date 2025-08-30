using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows;
using VRChatProximityApp.Services;
using VRChatProximityApp.Models;

namespace VRChatProximityApp;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window, INotifyPropertyChanged
{
    private readonly ProximityService _proximityService;
    private string _statusMessage = "Ready to connect to VRChat";

    public string StatusMessage
    {
        get => _statusMessage;
        set => SetProperty(ref _statusMessage, value);
    }

    public MainWindow()
    {
        InitializeComponent();
        
        _proximityService = new ProximityService();
        _proximityService.UserVisibilityChanged += OnUserVisibilityChanged;
        
        DataContext = _proximityService;
        
        // Handle window closing to properly dispose resources
        Closing += OnWindowClosing;
    }

    private async void StartButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            StatusMessage = "Connecting to VRChat...";
            await _proximityService.StartAsync();
            StatusMessage = "Connected! Proximity detection active.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Connection failed: {ex.Message}";
            MessageBox.Show($"Failed to connect to VRChat: {ex.Message}", 
                          "Connection Error", 
                          MessageBoxButton.OK, 
                          MessageBoxImage.Error);
        }
    }

    private void StopButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            _proximityService.Stop();
            StatusMessage = "Disconnected from VRChat.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error stopping service: {ex.Message}";
        }
    }

    private void OnUserVisibilityChanged(object? sender, VRChatUser user)
    {
        // This could be used to trigger additional actions when user visibility changes
        // For example: logging, notifications, sounds, etc.
        StatusMessage = user.IsVisible ? 
            $"User '{user.DisplayName}' is now visible" :
            $"User '{user.DisplayName}' is now hidden";
    }

    private void OnWindowClosing(object? sender, CancelEventArgs e)
    {
        _proximityService?.Stop();
        _proximityService?.Dispose();
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
