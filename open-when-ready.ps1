# Ждёт готовности сервера NetworkMap и открывает браузер.
# Вызывается автоматически из start.bat.
for ($i = 0; $i -lt 40; $i++) {
    try {
        $c = New-Object Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', 8790)
        $c.Close()
        Start-Process 'http://localhost:8790'
        break
    } catch {
        Start-Sleep -Milliseconds 700
    }
}
