do  

    --协议名称为INT，在Packet Details窗格显示为QAX.TZ INT
    local F_INT =  Proto("INT", "In-band Network Telemetry")


    --协议的各个字段
    --这里的base是显示的时候的进制
    --8/16/24/32/64/string, default:32
    --base.DEC/HEX/OCT/DEC_HEX/HEX_DEC, default:base.DEC

    local f_type=ProtoField.uint8("INT.Type", "Type", base.HEX)
    local f_count=ProtoField.uint8("INT.Count", "Count", base.DEC)
    local f_bitmap_need=ProtoField.uint32("INT.Bitmap_need", "Bitmap_need", base.HEX)


    --这里把INT协议的全部字段都加到FINT这个变量的fields字段里
    local f_bitmap_add=ProtoField.uint32("INT.Bitmap_add", "Bitmap_add", base.HEX)
    local f_length=ProtoField.uint8("INT.Length", "Length", base.DEC)
    local f_metadata=ProtoField.bytes("INT.Metadata", "Metadata")

    F_INT.fields = {
        f_type,
        f_bitmap_need,
        f_count,

        f_bitmap_add,
        f_length,
        f_metadata,
    }


    --这里是获取data这个解析器
    local data_dis = Dissector.get("data")

    local function INT_dissector(buf, pkt, root)
        local buf_len = buf:len();
        --先检查报文长度，太短的不是我们的协议
        if buf_len < 5 then return false end

        --现在知道是我的协议了，放心大胆添加Packet Details
        local t = root:add(F_INT, buf)

        pkt.cols.protocol = "in-band network telemetry"

        --取出字段的值, 并分配给“类型”子树
        local int_type_st = t:add(F_INT,buf,"INT Header")

        local ofset = 0

        local v_type = buf(ofset,1):bitfield(0,2)
        v_type = tonumber(tostring(v_type), 16)

        local v_count = buf(ofset,1):bitfield(2,6)
        v_count = tonumber(tostring(v_count), 16)

        ofset = ofset + 1

        local v_bitmap_need = buf(ofset,1+v_type)
        v_bitmap_need = tonumber(tostring(v_bitmap_need), 16)
        ofset = ofset + 1 + v_type

        int_type_st:add_le(f_type, v_type)
        int_type_st:add_le(f_count, v_count)
        int_type_st:add_le(f_bitmap_need, v_bitmap_need)

        --取出字段的值，并分配给“信息”子树
        local int_infos_st = t:add(F_INT,buf, "INT Data")


        local cn = 0
        while (cn < v_count)
        do
            --为新一段遥测信息构建子子树
            local int_infos_sst = int_infos_st:add(F_INT,buf," int data "..tostring(cn+1))

            --取出该段遥测信息
            local v_bitmap_add = buf(ofset, 1 + v_type)
            ofset = ofset + 1 + v_type

            local v_length = buf(ofset,1)
            v_length = tonumber(tostring(v_length), 16)
            ofset = ofset + 1

            local v_metadata = buf(ofset, v_length)
            ofset = ofset + v_length


            cn = cn + 1

            int_infos_sst:add_le(f_bitmap_add, v_bitmap_add)
            int_infos_sst:add_le(f_length, v_length)
            int_infos_sst:add_le(f_metadata, v_metadata)

        end

        --继续解析IPv4
        local raw_data = buf(ofset, buf_len-ofset)
        Dissector.get("ip"):call(raw_data:tvb(), pkt, root)
        pkt.cols.protocol:append("-INT")

        return true
    end

    --这段代码是目的Packet符合条件时，被Wireshark自动调用的，是p_INT的成员方法
    function F_INT.dissector(buf, pkt, root)
        if INT_dissector(buf,pkt,root) then
            --valid INT diagram
        else
            --data这个dissector几乎是必不可少的；当发现不是我的协议时，就应该调用data
            data_dis:call(buf,pkt,root)
        end
    end

    local eth_encap_table = DissectorTable.get("ethertype")
    --因为我们的自定义协议的接受以太网帧类型为0x1727=5927，所以这里只需要添加到“ethertype”
    --这个DissectorTable里，并且指定值为5927即可。
    eth_encap_table:add(5927, F_INT)


end