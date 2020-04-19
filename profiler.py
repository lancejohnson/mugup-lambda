import cProfile, pstats, io


def profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

# running process_lastnames with profiler
# most time (see cumtime -> cumulative time) is spent in boto/requesting -> the second lambda function
# 1.2 sec are spent in         1    0.000    0.000    1.126    1.126 /Users/rich/code/src/github.com/mugup-lambda/handler.py:268(create_amazon_upload_file)
# which we should be able to optimize to miliseconds
"""
/Users/rich/code/src/github.com/mugup-lambda/venv/bin/python /Users/rich/code/src/github.com/mugup-lambda/handler.py
Execution started
Format dict for csv printing
Write listing information to txt file
         87853 function calls (85218 primitive calls) in 38.245 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   38.245   38.245 /Users/rich/code/src/github.com/mugup-lambda/handler.py:243(process_lastnames)
        3    0.000    0.000   37.403   12.468 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:308(_api_call)
        3    0.000    0.000   37.403   12.468 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:581(_make_api_call)
        3    0.000    0.000   37.400   12.467 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:630(_make_request)
        3    0.000    0.000   37.400   12.467 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:99(make_request)
        3    0.000    0.000   37.400   12.467 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:130(_send_request)
        3    0.000    0.000   37.394   12.465 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:160(_get_response)
        3    0.000    0.000   37.393   12.464 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:185(_do_get_response)
        3    0.000    0.000   37.392   12.464 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:243(_send)
        3    0.000    0.000   37.392   12.464 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/httpsession.py:246(send)
        3    0.000    0.000   37.391   12.464 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:499(urlopen)
        3    0.000    0.000   37.389   12.463 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:356(_make_request)
        3    0.000    0.000   36.449   12.150 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1277(getresponse)
        3    0.000    0.000   36.449   12.150 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:289(begin)
       28    0.000    0.000   36.448    1.302 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/socket.py:575(readinto)
       28    0.000    0.000   36.448    1.302 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:1038(recv_into)
        3    0.000    0.000   36.448   12.149 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:256(_read_status)
       28    0.000    0.000   36.448    1.302 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:899(read)
       28    0.000    0.000   36.448    1.302 {method 'readline' of '_io.BufferedReader' objects}
       28   36.448    1.302   36.448    1.302 {method 'read' of '_ssl._SSLSocket' objects}
        1    0.000    0.000    1.126    1.126 /Users/rich/code/src/github.com/mugup-lambda/handler.py:268(create_amazon_upload_file)
        3    0.000    0.000    0.807    0.269 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:968(_validate_conn)
        2    0.000    0.000    0.807    0.404 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connection.py:306(connect)
        1    0.000    0.000    0.679    0.679 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/s3/inject.py:624(download_fileobj)
       36    0.678    0.019    0.678    0.019 {method 'acquire' of '_thread.lock' objects}
        2    0.000    0.000    0.678    0.339 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/threading.py:534(wait)
        2    0.000    0.000    0.678    0.339 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/threading.py:264(wait)
        1    0.000    0.000    0.674    0.674 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/s3transfer/futures.py:101(result)
        1    0.000    0.000    0.674    0.674 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/s3transfer/futures.py:249(result)
        2    0.000    0.000    0.527    0.263 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/ssl_.py:299(ssl_wrap_socket)
        2    0.000    0.000    0.502    0.251 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:399(wrap_socket)
        2    0.000    0.000    0.502    0.251 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:793(_create)
        2    0.000    0.000    0.501    0.251 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:1101(do_handshake)
        2    0.501    0.251    0.501    0.251 {method 'do_handshake' of '_ssl._SSLSocket' objects}
        2    0.000    0.000    0.280    0.140 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connection.py:146(_new_conn)
        2    0.000    0.000    0.280    0.140 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/connection.py:33(create_connection)
        2    0.241    0.120    0.241    0.120 {method 'connect' of '_socket.socket' objects}
        2    0.000    0.000    0.161    0.080 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/__init__.py:85(client)
        2    0.000    0.000    0.139    0.069 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/session.py:185(client)
        2    0.000    0.000    0.139    0.069 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/session.py:711(create_client)
        3    0.000    0.000    0.133    0.044 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1226(request)
        3    0.000    0.000    0.133    0.044 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:84(_send_request)
        3    0.000    0.000    0.133    0.044 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1231(_send_request)
        3    0.000    0.000    0.132    0.044 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1213(endheaders)
        3    0.000    0.000    0.132    0.044 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:109(_send_output)
        2    0.000    0.000    0.131    0.066 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:142(wait_for_read)
        2    0.000    0.000    0.131    0.066 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:90(poll_wait_for_socket)
        2    0.000    0.000    0.131    0.066 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:42(_retry_on_intr)
        2    0.000    0.000    0.131    0.066 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:102(do_poll)
        2    0.131    0.066    0.131    0.066 {method 'poll' of 'select.poll' objects}
        2    0.000    0.000    0.113    0.057 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:70(create_client)
        3    0.000    0.000    0.059    0.020 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/utils.py:1679(get_environ_proxies)
        3    0.000    0.000    0.057    0.019 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/utils.py:1686(should_bypass_proxies)
        3    0.000    0.000    0.057    0.019 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2599(proxy_bypass)
        2    0.000    0.000    0.056    0.028 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:278(_get_client_args)
        2    0.000    0.000    0.056    0.028 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/args.py:68(get_client_args)
        3    0.000    0.000    0.056    0.019 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2585(proxy_bypass_macosx_sysconf)
        2    0.000    0.000    0.051    0.026 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:251(create_endpoint)
        3    0.000    0.000    0.050    0.017 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2522(_proxy_bypass_macosx_sysconf)
        2    0.000    0.000    0.050    0.025 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:284(_get_proxies)
        3    0.047    0.016    0.049    0.016 {built-in method _socket.gethostbyname}
        2    0.000    0.000    0.038    0.019 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/socket.py:731(getaddrinfo)
        2    0.038    0.019    0.038    0.019 {built-in method _socket.getaddrinfo}
     15/5    0.000    0.000    0.032    0.006 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/loaders.py:126(_wrapper)
    86/72    0.000    0.000    0.030    0.000 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/session.py:916(get_component)
    28/25    0.000    0.000    0.028    0.001 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/hooks.py:354(emit)
     38/4    0.000    0.000    0.027    0.007 <frozen importlib._bootstrap>:978(_find_and_load)
     38/4    0.000    0.000    0.027    0.007 <frozen importlib._bootstrap>:948(_find_and_load_unlocked)
     15/3    0.000    0.000    0.027    0.009 {built-in method builtins.__import__}
     
     ....
     
"""

# running 1 lastname on my machine
# render_mug takes 20 secs out of 32, the rest is uploading
# transform is costly indeed with ~7 secs, we may cache some of the calculations
"""
render_and_upload started...
         5911487 function calls (5903592 primitive calls) in 32.626 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   32.627   32.627 /Users/rich/code/src/github.com/mugup-lambda/handler.py:1060(profile_render_and_upload)
        1    0.010    0.010   32.627   32.627 /Users/rich/code/src/github.com/mugup-lambda/handler.py:12(render_and_upload_lastname_mug)
        1    0.019    0.019   20.389   20.389 /Users/rich/code/src/github.com/mugup-lambda/handler.py:24(render_mug)
        6    0.000    0.000   12.279    2.047 /Users/rich/code/src/github.com/mugup-lambda/handler.py:15(load_file_from_s3)
        1    0.001    0.001   12.228   12.228 /Users/rich/code/src/github.com/mugup-lambda/handler.py:197(upload_mug_to_s3)
        6    0.000    0.000   12.002    2.000 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/s3/inject.py:624(download_fileobj)
       78   11.997    0.154   11.997    0.154 {method 'acquire' of '_thread.lock' objects}
       12    0.000    0.000   11.996    1.000 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/threading.py:534(wait)
       12    0.000    0.000   11.996    1.000 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/threading.py:264(wait)
        6    0.000    0.000   11.979    1.997 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/s3transfer/futures.py:101(result)
        6    0.000    0.000   11.979    1.997 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/s3transfer/futures.py:249(result)
        4    0.000    0.000    9.618    2.405 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:308(_api_call)
        4    0.000    0.000    9.618    2.405 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:581(_make_api_call)
        4    0.000    0.000    9.608    2.402 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:630(_make_request)
        4    0.000    0.000    9.608    2.402 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:99(make_request)
        4    0.000    0.000    9.608    2.402 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:130(_send_request)
        4    0.000    0.000    9.602    2.401 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:160(_get_response)
        4    0.000    0.000    9.601    2.400 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:185(_do_get_response)
        4    0.000    0.000    9.600    2.400 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:243(_send)
        4    0.000    0.000    9.600    2.400 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/httpsession.py:246(send)
        4    0.000    0.000    9.597    2.399 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:499(urlopen)
        4    0.000    0.000    9.596    2.399 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:356(_make_request)
        4    0.000    0.000    7.780    1.945 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1226(request)
        4    0.000    0.000    7.780    1.945 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:84(_send_request)
        4    0.000    0.000    7.780    1.945 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1231(_send_request)
        4    0.000    0.000    7.779    1.945 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1213(endheaders)
        4    0.000    0.000    7.779    1.945 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:109(_send_output)
        4    0.000    0.000    7.280    1.820 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:157(_handle_expect_response)
        8    0.000    0.000    7.279    0.910 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:198(send)
        8    0.002    0.000    7.279    0.910 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:948(send)
        4    0.000    0.000    7.278    1.820 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/awsrequest.py:194(_send_message_body)
      430    0.004    0.000    7.275    0.017 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:1001(sendall)
      430    0.001    0.000    7.270    0.017 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:974(send)
      430    7.269    0.017    7.269    0.017 {method 'write' of '_ssl._SSLSocket' objects}
        1    3.109    3.109    7.018    7.018 /Users/rich/code/src/github.com/mugup-lambda/handler.py:49(transform_lastname)
        4    0.000    0.000    2.600    0.650 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:2057(save)
        4    0.002    0.000    2.600    0.650 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/PngImagePlugin.py:1148(_save)
        4    0.001    0.000    2.597    0.649 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/ImageFile.py:474(_save)
       54    2.592    0.048    2.592    0.048 {method 'encode' of 'ImagingEncoder' objects}
  1147593    2.022    0.000    2.022    0.000 /Users/rich/code/src/github.com/mugup-lambda/handler.py:57(plot_deflected_point)
  1147592    0.739    0.000    1.859    0.000 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:1684(putpixel)
        4    0.000    0.000    1.433    0.358 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:1277(getresponse)
        4    0.000    0.000    1.433    0.358 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:289(begin)
      104    0.000    0.000    1.432    0.014 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/socket.py:575(readinto)
      104    0.000    0.000    1.431    0.014 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:1038(recv_into)
      104    0.000    0.000    1.431    0.014 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:899(read)
        4    0.000    0.000    1.431    0.358 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/http/client.py:256(_read_status)
      104    1.431    0.014    1.431    0.014 {method 'read' of '_ssl._SSLSocket' objects}
       32    0.000    0.000    1.431    0.045 {method 'readline' of '_io.BufferedReader' objects}
        1    0.002    0.002    1.415    1.415 /Users/rich/code/src/github.com/mugup-lambda/handler.py:29(draw_lastname)
  1147626    0.531    0.000    0.738    0.000 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:809(load)
       15    0.001    0.000    0.615    0.041 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/ImageFile.py:140(load)
      249    0.604    0.002    0.604    0.002 {method 'decode' of 'ImagingDecoder' objects}
        7    0.000    0.000    0.499    0.071 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:142(wait_for_read)
        7    0.000    0.000    0.499    0.071 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:90(poll_wait_for_socket)
        7    0.000    0.000    0.499    0.071 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:42(_retry_on_intr)
        7    0.000    0.000    0.499    0.071 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/wait.py:102(do_poll)
        7    0.499    0.071    0.499    0.071 {method 'poll' of 'select.poll' objects}
        4    0.000    0.000    0.402    0.100 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:1418(paste)
        4    0.000    0.000    0.382    0.096 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connectionpool.py:968(_validate_conn)
        1    0.000    0.000    0.382    0.382 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connection.py:306(connect)
  1147592    0.381    0.000    0.381    0.000 {method 'putpixel' of 'ImagingCore' objects}
        8    0.000    0.000    0.381    0.048 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:615(_ensure_mutable)
        4    0.004    0.001    0.381    0.095 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:609(_copy)
      4/2    0.004    0.001    0.361    0.180 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:1814(resize)
        2    0.294    0.147    0.294    0.147 {method 'resize' of 'ImagingCore' objects}
        7    0.000    0.000    0.285    0.041 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/__init__.py:85(client)
        7    0.000    0.000    0.263    0.038 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/boto3/session.py:185(client)
        7    0.000    0.000    0.263    0.038 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/session.py:711(create_client)
        1    0.000    0.000    0.256    0.256 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/ssl_.py:299(ssl_wrap_socket)
        1    0.000    0.000    0.251    0.251 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/ImageDraw.py:453(Draw)
        1    0.000    0.000    0.251    0.251 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/ImageDraw.py:48(__init__)
        1    0.000    0.000    0.248    0.248 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:399(wrap_socket)
        1    0.000    0.000    0.248    0.248 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:793(_create)
        1    0.000    0.000    0.248    0.248 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/ssl.py:1101(do_handshake)
        1    0.248    0.248    0.248    0.248 {method 'do_handshake' of '_ssl._SSLSocket' objects}
        7    0.000    0.000    0.237    0.034 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:70(create_client)
  1147621    0.207    0.000    0.207    0.000 {method 'pixel_access' of 'ImagingCore' objects}
        7    0.000    0.000    0.166    0.024 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/client.py:278(_get_client_args)
        7    0.000    0.000    0.166    0.024 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/args.py:68(get_client_args)
        8    0.000    0.000    0.157    0.020 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/utils.py:1679(get_environ_proxies)
        8    0.000    0.000    0.152    0.019 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/utils.py:1686(should_bypass_proxies)
        8    0.000    0.000    0.152    0.019 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2599(proxy_bypass)
        7    0.000    0.000    0.151    0.022 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:251(create_endpoint)
        8    0.000    0.000    0.149    0.019 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2585(proxy_bypass_macosx_sysconf)
        7    0.000    0.000    0.148    0.021 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/botocore/endpoint.py:284(_get_proxies)
        8    0.000    0.000    0.142    0.018 /Users/rich/.pyenv/versions/3.7.0/lib/python3.7/urllib/request.py:2522(_proxy_bypass_macosx_sysconf)
        8    0.138    0.017    0.140    0.018 {built-in method _socket.gethostbyname}
        1    0.000    0.000    0.126    0.126 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/connection.py:146(_new_conn)
        1    0.000    0.000    0.126    0.126 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/urllib3/util/connection.py:33(create_connection)
        1    0.125    0.125    0.125    0.125 {method 'connect' of '_socket.socket' objects}
        4    0.000    0.000    0.063    0.016 /Users/rich/code/src/github.com/mugup-lambda/venv/lib/python3.7/site-packages/PIL/Image.py:859(convert)
        4    0.063    0.016    0.063    0.016 {method 'convert' of 'ImagingCore' objects}
"""