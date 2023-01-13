template = """
<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-GB">
​
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Harp</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
​
    <style type="text/css">
        a[x-apple-data-detectors] {
            color: inherit !important;
        }
    </style>
​
</head>
​
<body style="margin: 0; padding: 0; background: #ECF0F7;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td style="padding: 80px 0 30px 0;">
​
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%"
                    style="border-collapse: collapse;max-width: 600px">
                    <tr>
                        <td align="center" style="background: #ffffff;border-radius: 12px 12px 0 0;">
                            <img src="https://harpia.io/wp-content/uploads/2021/05/logo.png" alt="Harp" width="600"
                                height="76" style="display: block;max-width: 100%;" />
                        </td>
                    </tr>
                    <tr>
                        <td bgcolor="#ffffff" style="padding: 40px; border-radius: 0 0 12px 12px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%"
                                style="border-collapse: collapse;">
                                <tr>
                                    <td
                                        style="border-radius: 12px; color: #153643; font-family: Arial, sans-serif; background: #F4F8FC; padding: 30px; font-size: 16px; text-align: center; line-height: 24px;">
                                        <p style="text-align: center;font-size: 2rem;font-weight: 700;margin: 1rem 0 2rem">Welcome</p>
                                        <img src="https://harpia.io/wp-content/uploads/2021/05/welcome.png"
                                            alt="Welcome">
                                        <p style="text-align: center;margin: 20px 0 10px;">We’re excited to have you get started. First, you need<br>to confirm your account. Just press the button below.</p>
                                        <a href="{confirmation_endpoint}"
                                            style="display: inline-block;margin: 20px auto;background: #00C284;color: #fff;font-weight: 700;text-decoration: none;border-radius: 6px;padding: 13px 20px;font-size: 1rem;">Confirm
                                            Account</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
​
                </table>
​
            </td>
        </tr>
    </table>
</body>
​
</html>
"""