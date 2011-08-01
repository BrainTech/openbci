import org.signalml.multiplexer.protocol.SvarogConstants;
import org.signalml.multiplexer.protocol.SvarogProtocol.Sample;
import org.signalml.multiplexer.protocol.SvarogProtocol.SampleVector;
import org.signalml.multiplexer.protocol.SvarogProtocol.SampleOrBuilder;

import com.google.protobuf.ByteString;
import com.google.protobuf.InvalidProtocolBufferException;

public class ProtobufTest {
	public static void main(String[] args) throws InvalidProtocolBufferException {
	    if (args.length != 2) {
		System.out.println("Usage: ./protobuf_test <num samples> <num channels> ");
		return;
	    }
	    int num_of_channels = Integer.decode(args[1]);
	    int num_of_samples = Integer.decode(args[0]);

	    //Create one vector with some values
	    SampleVector.Builder sample_vec = SampleVector.newBuilder();
	    SampleVector msg = null;
	    Sample.Builder s = null;

	    for (int i=0; i<num_of_channels; i++) {
		s = Sample.newBuilder();
		s.setValue((double) i);
		s.setTimestamp(System.currentTimeMillis()/1000.0);
		sample_vec.addSamples(s);
	    }

	    // Want to print sth out?
	    /*for (int i=0;i < num_of_channels; i++) {
	      Sample s = sample_vec.getSamples(i);
	      System.out.println(s.getValue());
	      }*/

	    //Packing test ...
	    ByteString b_sample_vec = sample_vec.build().toByteString(), b_msg;
	    System.out.println("Approx. serialized sample vector size: "+b_sample_vec.size());
	    System.out.println("Start packing test ...");
	    double start_time = System.currentTimeMillis()/1000.0, t, end_time;
	    for (int i = 0; i < num_of_samples; i ++) {
		sample_vec = SampleVector.newBuilder();
		for (int j=0; j<num_of_channels; j++) {
		    s = Sample.newBuilder();
		    s.setValue((double) j);
		    s.setTimestamp(System.currentTimeMillis()/1000.0);
		    sample_vec.addSamples(s);
		    }
		/* alternative, should-be-but-isnt faster version
		for (int j=0; j<num_of_channels; j++) {
		    s = sample_vec.getSamplesBuilder(j);
		    s.setValue((double) i);
		    s.setTimestamp(System.currentTimeMillis()/1000.0);
		    }
		*/
		b_msg = sample_vec.build().toByteString();
	    };
	    end_time = System.currentTimeMillis()/1000.0;

	    System.out.println("End of packing test - time: "+(end_time - start_time));
	    System.out.println(" approx. sample rate: "+(num_of_samples / (end_time - start_time)));

	    
	    //Unpacking test...
	    System.out.println("Start Unpacking test ...");	    
	    start_time = System.currentTimeMillis()/1000.0;
	    for (int i = 0; i < num_of_samples; i ++) {
		msg = SampleVector.parseFrom(b_sample_vec);
	    };
	    end_time = System.currentTimeMillis()/1000.0;

	    System.out.println("End of Unpacking test - time: "+(end_time - start_time));
	    System.out.println(" approx. sample rate: "+(num_of_samples / (end_time - start_time)));

	    /*for (int i=0;i < num_of_channels; i++) {
	      Sample s = msg.getSamples(i);
	      System.out.println(s.getValue());
	      }
	    */

	}

}
