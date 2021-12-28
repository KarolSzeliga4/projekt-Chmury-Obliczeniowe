# -*- coding: utf-8 -*-

from app.main import app
if __name__ == "__main__":
  app.run()

# from app import app
# import os
#
# app.secret_key = os.urandom(24)
# port = int(os.environ.get('PORT', 5000))
# app.run(host='0.0.0.0', port=port)
