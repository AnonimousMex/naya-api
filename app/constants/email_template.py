def new_user_verification_code_email_tempalte(
    user_name: str,
    code: int,
) -> str:
    head = """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    @media only screen and (max-width: 600px) {
                        .content {
                            width: 100% !important;
                        }
                        .header, .footer {
                            text-align: center !important;
                        }
                    }
                </style>
            </head>
    """

    body = f"""
        <body style="margin:0; padding:0; background-color:#fff; font-family: sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#9C8AEF; ">
                <tr>
                    <td align="center" style="padding: 10px;">
                        <table role="presentation" width="630" cellpadding="0" cellspacing="0" border="0" style="background-color:#fff; border-radius: 30px; margin-bottom: 60px;">
                            <tr>
                                <td style="padding:20px;">
                                    <img src="https://i.ibb.co/kgWDj7nX/layer1.png" alt="NAYÁ  Logo" width="300" style="display: block; margin: auto; ">
                                </td>
                            </tr>
                            <tr>
                                <td style=" text-align: center; color: #655e5a; font-size: 27px; ">
                                    <p style="margin-bottom: 10px; font-weight: 700;">¡Bienvenido, {user_name}!</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-left:70px; padding-right:70px; text-align: center; color: #393533; font-size: 14px; font-weight: 600;">
                                    <p style="line-height: 1.5; margin-bottom: 35px; ">Estás a un paso de iniciar un emocionante viaje hacia el bienestar y la gestión de tus emociones. Para activar tu cuenta y comenzar a disfrutar
                                        de todo lo que ofrecemos, simplemente utiliza el siguiente código de activación:
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:20px; text-align:center; ">
                                    <span style="background-color: #6C5FC8; padding: 10px; padding: 15px 140px 15px 140px;  color: #fff; font-size: 30px; border-radius: 50px; border: 5px solid #dddddd; ">
                                        {code}
                                    </span>
                                </td>
                            </tr>
                            <tr >
                                <td style=" padding: 25px 100px 0px 100px; text-align:center; color: #C9C7C5;">
                                    <p style="margin:0; margin-bottom: 25px;">Por favor, introduce tu código de activación para activar tu cuenta y comenzar a usar todas las funciones de la aplicación.</p>
                                </td>
                            </tr>
                            <tr>
                                <td style=" padding: 5px 100px 0px 100px; text-align:center; font-size: 12px;">
                                    <p style="margin:0; margin-bottom: 65px;">Si necesitas ayuda, estamos aquí para ti</p>
                                </td>
                            </tr>
                            <tr>
                                <td style=" padding: 5px 210px 0px ; text-align:center; display: flex; flex-direction: row; align-items: center; justify-content: center; margin-bottom: 65px;">
                                    <a href="">
                                        <img src="https://mailmeteor.com/logos/assets/PNG/Gmail_Logo_512px.png" alt="Gmail Logo" style="width: 30px; height: 25px; ">
                                    </a>
                                    <hr style="height: 15px;">
                                    <a href="">
                                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Facebook_Logo_%282019%29.png/768px-Facebook_Logo_%282019%29.png" alt="Facebook Logo" style="width: 30px; height: 30px;">
                                    </a>
                                    <hr style="height: 15px;">
                                    <a href="" ;">
                                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/1200px-Instagram_icon.png" alt="Instagram Logo" style="width: 30px; height: 30px;">
                                    </a>
                                </td>
                            </tr>
                            <tr >
                                <td style="padding:35px 80px; background-color:#F6F1FF; text-align:center; border-bottom-left-radius: 30px; border-bottom-right-radius: 30px; font-weight: 600; color: #393533;">
                                    <p style="margin:0;">"Cada paso cuenta en tu camino hacia el bienestar. ¡Hoy es un gran comienzo!"</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td align="center">
                        <table role="footer" width="630" cellpadding="0" cellspacing="0" border="0"">
                            <tr>
                                <td style="text-align: center;">
                                    <img src="https://i.ibb.co/HWsphSX/suenaalgo-imagen.png" alt="Heart" style="width: 400px; height: 300px; margin-bottom: -20px; ">
                                </td>
                            </tr>
                            <tr>
                                <td style="text-align: center; background-color: #fff; border-radius: 100% 100% 0px 0px; padding: 20px 50px 20px 50px; position: relative;">
                                    <img src="https://i.ibb.co/kgWDj7nX/layer1.png" alt="NAYÁ Logo" width="170" style="display: block; margin: auto; margin-bottom: 20px;">
                                    <span style="font-size: 12px; color: #928D86;">¡Gracias por confiar en nosotros!</span><br>
                                    <span style="font-size: 12px; color: #928D86;">Este correo es parte de nuestro compromiso para ofrecerte una experiencia única.</span><br>
                                    <span style="font-size: 12px; color: #928D86;">Si tienes dudas o necesitas más información, contáctanos</span><br>
                                    <span style="font-size: 12px; color: #928D86;">en <a href="support@naya.com" style="color: #b067d2;">support@naya.com</a>.</span>
                                    <hr style="width: 500px; margin-top: 40px; margin-bottom: 40px; border: 0.5px solid rgb(237, 236, 236); ">
                                    <span style="font-size: 12px; color: #928D86;">NAYÁ, construyendto bienestar emocional.</span><br>
                                    <span style="font-size: 12px; color: #928D86;">Derechos reservados © 2024 NAYÁ</span>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
    """

    return f"{head}{body}"
