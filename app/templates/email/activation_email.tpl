<!DOCTYPE html>
<html>
<head>
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #2c3e50;
        color: #ffffff;
    }
    .container {
        width: 80%;
        margin: 0 auto;
        background-color: #8e44ad;
        padding: 20px;
        border-radius: 5px;
    }
    a {
        color: #ffffff;
        text-decoration: none;
    }
</style>
</head>
<body dir="rtl">
    <div class="container">
        <h1>سلام {{ user_name }},</h1>
        <p>با تشکر از ثبت‌نام شما در {{ site_name }}، لطفاً برای تایید ایمیل خود و فعال‌سازی حساب کاربری‌تان، روی لینک زیر کلیک کنید:</p>
        <p><a href="{{ email_verification_link }}">لینک تایید ایمیل</a></p>
        <p>اگر شما این درخواست را ارسال نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.</p>
        <p>با تشکر،</p>
        <p>تیم {{ site_name }}</p>
    </div>
</body>
</html>