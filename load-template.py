#!/usr/bin/env python

import json
import easypg
import re

easypg.config_name = 'bookserver'
'''
e.g.:
{"name": "William York Tindall",
"created": {"type": "/type/datetime", "value": "2008-04-01T03:28:50.625462"},
"death_date": "1981",
"last_modified": {"type": "/type/datetime", "value": "2010-04-10T23:35:59.317184"},
"latest_revision": 3,
"key": "/authors/OL529081A",
"birth_date": "1903",
"personal_name": "William York Tindall",
"type": {"key": "/type/author"},
"revision": 3}

'''
with open('data/sample-data/authors.json') as af:
    count = 1
    for line in af:
#        if count > 100:
#            break
        count += 1
        author = json.loads(line.strip())
        author_key = author['key']
        # print 'found author', author_key
        # put the author in your database
        with easypg.cursor() as cur:
            # first clean up book title
            try:
                author['name'] = author['name'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                print "No name for this author entry! Continuing..."
                continue


            if len(author['name']) > 255:
                print "This author's name (%s) is too long, not importing it for the moment! Continuing..." % author['name']
                continue

            if len(author['key']) > 255:
                print "This author's key (%s) is too long, not importing it for the moment! Continuing..." % author['key']
                continue
            # now check to see if we have an existing "author" entry
            #print "Checking to see if a author entry exists for %s..." % author['key']
            cur.execute('''
                SELECT author_id
                FROM author
                WHERE author_alias = %s
            ''', (author['key'],))

            if (cur.rowcount == 0):
                print "Inserting author name  %s along with key %s." % (author['name'], author['key'])                
                cur.execute('''
                  INSERT INTO author (author_name, author_alias)
                  VALUES(%s, %s)
                  RETURNING author_id
                ''', (author['name'], author['key']))
            else:
                print "Already an entry for this author key: %s..." % author['key']
            print "-----------------------\n\n"
'''
with open('works.json') as af:
    for line in af:
        work = json.loads(line.strip())
        work_key = work['key']
        print 'found work', work_key
        # put the work in your database
'''


with open('data/sample-data/books.json') as af:
    count = 1
    for line in af:
        if count > 1000:
            break
        count += 1
        book = json.loads(line.strip())
        book_key = book['key']
        # print 'found book', book_key
        # print book
        # put the book in your database
        with easypg.cursor() as cur:
            # first clean up book title
            try:
                book['title'] = book['title'].strip().encode('ascii', 'xmlcharrefreplace')
            except KeyError:
                print "No title for this book entry! Continuing..."
                continue


            if len(book['title']) > 250:
                print "This book's title (%s) is too long, not importing it for the moment! Continuing..." % book['title']
                continue

            # now check to see if we have an existing "book_core" entry
            #print "Checking to see if a book core entry exists for %s..." % book['title']
            cur.execute('''
                SELECT core_id
                FROM book_core
                WHERE book_title = %s
            ''', (book['title'],))

            if (cur.rowcount != 1):
                #print "No book core entry found, adding one now..."
                #too many, or no, matching book_core entries found -> make a new one
                cur.execute('''
                  INSERT INTO book_core (book_title, book_description, edition)
                  VALUES(%s, %s, %s)
                  RETURNING core_id
                ''', (book['title'], '', book['revision']))

            # Retrieve book_core_id for book insertion
            book_core_id = cur.fetchone()[0]
            #print "Book core ID obtained: %s!" % book_core_id

            # check to see what type of ISBN we have to work with, go with ISBN if possible
            # explanation of this type of structure at: http://stackoverflow.com/a/1592578/1431509
            try:
                book['isbn_13']
            except KeyError:
                try:
                    book['isbn_10']
                except KeyError:
                    print "%s has no ISBN!" % book['title']
                    book_isbn = []
                else:
                    book_isbn = book['isbn_10']
            else:
                book_isbn = book['isbn_13']

            try:
                book['number_of_pages']
            except KeyError:
                page_count = None
                print "%s has no page count!" % book['title']
            else:
                page_count = book['number_of_pages']

            try:
                book['physical_format']
            except KeyError:
                book_type = None
            else:
                book_type = book['physical_format']

            try:
                #print "Publish date is: %s." % book['publish_date']
                original_date = book['publish_date']
            except KeyError:
                print "%s has no publication date!" % book['title']
                publication_date = None
                original_date = None
            else:
                if re.match('\w* \d{1,2}, \d{4}', book['publish_date']):
                    m = re.match('(\w* \d{1,2}, \d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = m.groups()[0]
                elif re.match('\w* \d{4}', book['publish_date']):
                    m = re.match('(\w*) (\d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = "%s 01, %s" % (m.groups()[0], m.groups()[1])
                elif re.match('\d{4}', book['publish_date']):
                    m = re.match('(\d{4})', book['publish_date'])
                    # print m.groups()
                    publication_date = "January 01, %s" % m.groups()[0]
                else :
                    publication_date = None
            #print "Parsed publication_date is: %s (Original date: %s)." % (publication_date, original_date)
            # was getting output in this formatting "[u'9780110827667']" slicing off the excess
            # until I find whats going on
            # book_isbn = book_isbn[2:-2]
            for isbn in book_isbn:
                isbn = ''.join(x for x in isbn if x.isdigit())
                print "Inserting book title %s along with core_id %s (ISBN: %s - Date: %s)." % (book['title'], book_core_id, isbn, publication_date)
                cur.execute('''
                    INSERT INTO books (core_id, publication_date, isbn, book_type, page_count)
                    VALUES(%s, %s, %s, %s, %s)
                ''', (book_core_id, publication_date, isbn, book_type, page_count))

            # add author relationships if found
            try:
                for author in book['authors']:
                    position = 1
                    cur.execute('''
                    SELECT author_id
                    FROM author
                    WHERE author_alias = %s
                    ''', (author,))
                    if cur.rowcount != 1:
                        print "No valid matching author found for key: %s." % author
                    else:
                        author_id = cur.fetchone()[0]
                        cur.execute('''
                        INSERT INTO authorship (core_id, author_id, position)
                        VALUES(%s, %s)
                        RETURNING author_id
                        ''', (book_core_id, author_id, position))                        
            except KeyError:
                print "No authors found!"

            print "-----------------------\n\n"