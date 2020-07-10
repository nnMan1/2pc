/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package thrift

import (
	"context"
	"net"
	"time"
)

type TSocket struct {
	conn           *socketConn
	addr           net.Addr
	connectTimeout time.Duration
	socketTimeout  time.Duration
}

// NewTSocket creates a net.Conn-backed TTransport, given a host and port
//
// Example:
// 	trans, err := thrift.NewTSocket("localhost:9090")
func NewTSocket(hostPort string) (*TSocket, error) {
	return NewTSocketTimeout(hostPort, 0, 0)
}

// NewTSocketTimeout creates a net.Conn-backed TTransport, given a host and port
// it also accepts a timeout as a time.Duration
func NewTSocketTimeout(hostPort string, connTimeout time.Duration, soTimeout time.Duration) (*TSocket, error) {
	//conn, err := net.DialTimeout(network, address, timeout)
	addr, err := net.ResolveTCPAddr("tcp", hostPort)
	if err != nil {
		return nil, err
	}
	return NewTSocketFromAddrTimeout(addr, connTimeout, soTimeout), nil
}

// Creates a TSocket from a net.Addr
func NewTSocketFromAddrTimeout(addr net.Addr, connTimeout time.Duration, soTimeout time.Duration) *TSocket {
	return &TSocket{addr: addr, connectTimeout: connTimeout, socketTimeout: soTimeout}
}

// Creates a TSocket from an existing net.Conn
func NewTSocketFromConnTimeout(conn net.Conn, socketTimeout time.Duration) *TSocket {
	return &TSocket{conn: wrapSocketConn(conn), addr: conn.RemoteAddr(), socketTimeout: socketTimeout}
}

// Sets the connect timeout
func (p *TSocket) SetConnTimeout(timeout time.Duration) error {
	p.connectTimeout = timeout
	return nil
}

// Sets the socket timeout
func (p *TSocket) SetSocketTimeout(timeout time.Duration) error {
	p.socketTimeout = timeout
	return nil
}

func (p *TSocket) pushDeadline(read, write bool) {
	var t time.Time
	if p.socketTimeout > 0 {
		t = time.Now().Add(time.Duration(p.socketTimeout))
	}
	if read && write {
		p.conn.SetDeadline(t)
	} else if read {
		p.conn.SetReadDeadline(t)
	} else if write {
		p.conn.SetWriteDeadline(t)
	}
}

// Connects the socket, creating a new socket object if necessary.
func (p *TSocket) Open() error {
	if p.conn.isValid() {
		return NewTTransportException(ALREADY_OPEN, "Socket already connected.")
	}
	if p.addr == nil {
		return NewTTransportException(NOT_OPEN, "Cannot open nil address.")
	}
	if len(p.addr.Network()) == 0 {
		return NewTTransportException(NOT_OPEN, "Cannot open bad network name.")
	}
	if len(p.addr.String()) == 0 {
		return NewTTransportException(NOT_OPEN, "Cannot open bad address.")
	}
	var err error
	if p.conn, err = createSocketConnFromReturn(net.DialTimeout(
		p.addr.Network(),
		p.addr.String(),
		p.connectTimeout,
	)); err != nil {
		return NewTTransportException(NOT_OPEN, err.Error())
	}
	return nil
}

// Retrieve the underlying net.Conn
func (p *TSocket) Conn() net.Conn {
	return p.conn
}

// Returns true if the connection is open
func (p *TSocket) IsOpen() bool {
	return p.conn.IsOpen()
}

// Closes the socket.
func (p *TSocket) Close() error {
	// Close the socket
	if p.conn != nil {
		err := p.conn.Close()
		if err != nil {
			return err
		}
		p.conn = nil
	}
	return nil
}

//Returns the remote address of the socket.
func (p *TSocket) Addr() net.Addr {
	return p.addr
}

func (p *TSocket) Read(buf []byte) (int, error) {
	if !p.conn.isValid() {
		return 0, NewTTransportException(NOT_OPEN, "Connection not open")
	}
	p.pushDeadline(true, false)
	// NOTE: Calling any of p.IsOpen, p.conn.read0, or p.conn.IsOpen between
	// p.pushDeadline and p.conn.Read could cause the deadline set inside
	// p.pushDeadline being reset, thus need to be avoided.
	n, err := p.conn.Read(buf)
	return n, NewTTransportExceptionFromError(err)
}

func (p *TSocket) Write(buf []byte) (int, error) {
	if !p.conn.isValid() {
		return 0, NewTTransportException(NOT_OPEN, "Connection not open")
	}
	p.pushDeadline(false, true)
	return p.conn.Write(buf)
}

func (p *TSocket) Flush(ctx context.Context) error {
	return nil
}

func (p *TSocket) Interrupt() error {
	if !p.conn.isValid() {
		return nil
	}
	return p.conn.Close()
}

func (p *TSocket) RemainingBytes() (num_bytes uint64) {
	const maxSize = ^uint64(0)
	return maxSize // the truth is, we just don't know unless framed is used
}
