ó
c\Tc           @   sy   d  Z  d d l m Z m Z d d l Z d d l m Z e e d  Z e d    Z	 d   Z
 e d k ru e
   n  d S(	   sj   
EasyPG - a module to make it easier to connect to PostgreSQL with different configurations.

:version: 7
iÿÿÿÿ(   t   closingt   contextmanagerN(   t   SafeConfigParserc         K   sn   t    } | j d  t | j    } | j | j d   t j |   } | | _ |  rf t |  S| Sd S(   s}  
    Connects to the database.  Configuration is read from the configuration
    file ``pgapp.cfg``, if available.

    :param context: whether to wrap the connection in an auto-closing context manager.
    :param kwargs: Default configuration parameters.
    :return: The database connection, wrapped in a context manager for a ``with`` block.
    :rtype: psycopg2.Connection
    s	   pgapp.cfgt   databaseN(	   R   t   readt   dictt   itemst   updatet   psycopg2t   connectt
   autocommitR    (   t   contextR
   t   kwargst   cpt   optst   cxn(    (    s)   /home/jeffrey/workspace/booknet/easypg.pyR	      s    
		
c          k   sK   t  d t |   } z' | j   } z	 | VWd | j   XWd | j   Xd S(   sÉ   
    Context-managed cursor and database connection.  This will yield a cursor,
    and close both the cursor and the database connection.
    :param kwargs: The connection arguments.
    :return:
    R   N(   R	   t   Falset   cursort   close(   R   t   dbct   cur(    (    s)   /home/jeffrey/workspace/booknet/easypg.pyR       s    	c          C   s   t     }  d GHWd  QXd  S(   Ns   connected to database(   R   (   R   (    (    s)   /home/jeffrey/workspace/booknet/easypg.pyt   demo2   s    t   __main__(   t   __doc__t
   contextlibR    R   R   t   ConfigParserR   t   TrueR	   R   R   t   __name__(    (    (    s)   /home/jeffrey/workspace/booknet/easypg.pyt   <module>   s   	